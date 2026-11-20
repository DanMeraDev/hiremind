"""Paso 6: comparar con la vacante y puntuar.  Puntaje = Σ wᵢ · sᵢ

Lo hace Python con reglas fijas; el LLM no asigna notas.
sᵢ: cumple = 1, parcial = 0,5, no identificado = 0.
Solo cuentan los datos cuya cita fue verificada en el CV.
"""
from __future__ import annotations

import re
from datetime import date

from .modelos import (ORDEN_FORMACION, ORDEN_IDIOMA, Criterio, ExtraccionCV, ResultadoCriterio,
                      Vacante)
from .texto import contiene_palabra, normalizar

NOMBRE_NIVEL = {"bachillerato": "bachillerato", "tecnico": "técnico", "tecnologo": "tecnólogo",
                "tercer_nivel": "tercer nivel", "cuarto_nivel": "cuarto nivel", "otro": "otro"}


def _verificados(ext: ExtraccionCV, ver: dict[str, list[bool]], seccion: str) -> list:
    return [it for it, ok in zip(getattr(ext, seccion), ver[seccion]) if ok]


def _coincide(textos: list[str], palabras: list[str]) -> bool:
    if not palabras:
        return True
    t = normalizar(" ".join(textos))
    return any(contiene_palabra(t, p) for p in palabras)


# ---------------------------------------------------------------- fechas
def _a_mes(valor: str, hoy: date) -> int | None:
    """'2021-03' -> índice de mes; 'actual' -> hoy. None si no se entiende."""
    v = normalizar(valor)
    if v in ("actual", "actualidad", "presente", "a la fecha", "hoy"):
        return hoy.year * 12 + hoy.month - 1
    m = re.match(r"^(\d{4})(?:[-/](\d{1,2}))?", v)
    if not m:
        return None
    anio, mes = int(m.group(1)), int(m.group(2) or 1)
    if not (1950 <= anio <= hoy.year + 1 and 1 <= mes <= 12):
        return None
    return anio * 12 + mes - 1


_FECHA = re.compile(r"\b((?:19|20)\d{2}(?:[-/](?:0?[1-9]|1[0-2]))?)\b|\b(actualidad|actual|presente|la fecha)\b")


def fechas_de_cita(cita: str, inicio: str, fin: str) -> tuple[str, str]:
    """Si la cita trae el periodo, Python lo toma de ahí (el modelo a veces confunde las fechas)."""
    hallados = [m.group(1) or "actual" for m in _FECHA.finditer(normalizar(cita))]
    if len(hallados) >= 2:
        return hallados[0], hallados[1]
    if len(hallados) == 1 and hallados[0] != "actual":
        return hallados[0], fin
    return inicio, fin


def anios_experiencia(intervalos: list[tuple[int, int]]) -> float:
    """Suma de meses sin contar dos veces los periodos que se solapan."""
    total, fin_actual = 0, None
    for ini, fin in sorted(intervalos):
        fin += 1  # el mes de fin cuenta completo
        if fin_actual is None or ini >= fin_actual:
            total += fin - ini
            fin_actual = fin
        elif fin > fin_actual:
            total += fin - fin_actual
            fin_actual = fin
    return total / 12


# ---------------------------------------------------------------- formación: nivel decidido por Python
# El modelo pequeño clasifica mal el nivel (p. ej. "Ingeniería" como tecnólogo), así que
# Python lo deduce del título; el nivel del modelo solo se usa si el título no dice nada.
_REGLAS_NIVEL = [
    ("otro", r"curso|certificacion|certificado|taller|diplomado|seminario|bootcamp"),
    ("cuarto_nivel", r"maestria|magister|master|msc|mba|doctorado|phd|especializacion|especialista"),
    ("tercer_nivel", r"ingenieria|ingeniero|ingeniera|licenciatura|licenciado|licenciada|economista"
                     r"|abogado|abogada|arquitectura|medicina|odontologia|psicologia|cpa"),
    ("tecnologo", r"tecnologia superior|tecnologo|tecnologa|tecnologia"),
    ("tecnico", r"tecnico superior|tecnico|tecnica"),
    ("bachillerato", r"bachillerato|bachiller"),
]
_EN_CURSO = re.compile(r"\b(cursando|en curso|semestre|estudiante|egresado|egresada|por culminar)\b")


def nivel_formacion(f) -> str:
    for texto in (f.titulo, f.cita):
        t = normalizar(texto)
        for nivel, patron in _REGLAS_NIVEL:
            if re.search(r"\b(?:" + patron + r")\b", t):
                return nivel
    return f.nivel


def en_curso(f) -> bool:
    return _EN_CURSO.search(normalizar(f"{f.titulo} {f.cita}")) is not None


# ---------------------------------------------------------------- reglas por tipo
def _secundarias(ext, ver) -> list[str]:
    """Textos de proyectos y cursos: la evidencia que viene de ahí vale como parcial."""
    out = [normalizar(f"{p.nombre} {p.descripcion} {p.cita}") for p in _verificados(ext, ver, "proyectos")]
    out += [normalizar(f.cita) for f in _verificados(ext, ver, "formacion") if nivel_formacion(f) == "otro"]
    return out


def _sale_de(cita: str, secundarias: list[str]) -> bool:
    c = normalizar(cita)
    return len(c) >= 15 and any(c in s or s in c for s in secundarias)


def _habilidad(c: Criterio, ext, ver) -> ResultadoCriterio:
    sec = _secundarias(ext, ver)
    habilidades = [h for h in _verificados(ext, ver, "habilidades")
                   if _coincide([h.nombre, h.cita], c.palabras_clave)]
    fuertes = [h for h in habilidades if not _sale_de(h.cita, sec)]
    if fuertes:
        return _res(c, "cumple", "Aparece en habilidades", [h.cita for h in fuertes])
    experiencia = [e for e in _verificados(ext, ver, "experiencia")
                   if _coincide([e.cargo, e.descripcion, e.cita], c.palabras_clave)]
    if experiencia:
        return _res(c, "cumple", "Aparece en experiencia laboral", [e.cita for e in experiencia])
    secundarias = [h.cita for h in habilidades]
    secundarias += [p.cita for p in _verificados(ext, ver, "proyectos")
                    if _coincide([p.nombre, p.descripcion, p.cita], c.palabras_clave)]
    secundarias += [f.cita for f in _verificados(ext, ver, "formacion")
                    if nivel_formacion(f) == "otro" and _coincide([f.titulo, f.cita], c.palabras_clave)]
    if secundarias:
        return _res(c, "parcial", "Solo aparece en proyectos o cursos, no en experiencia laboral",
                    list(dict.fromkeys(secundarias)))
    return _res(c, "no_identificado", "No se encontró evidencia verificada en el CV")


def _experiencia(c: Criterio, ext, ver, hoy: date) -> ResultadoCriterio:
    intervalos, citas = [], []
    for e in _verificados(ext, ver, "experiencia"):
        if not _coincide([e.cargo, e.descripcion, e.cita], c.palabras_clave):
            continue
        inicio, fin_txt = fechas_de_cita(e.cita, e.inicio, e.fin)
        ini, fin = _a_mes(inicio, hoy), _a_mes(fin_txt, hoy)
        if ini is None or fin is None or fin < ini:
            continue
        intervalos.append((ini, fin))
        citas.append(e.cita)
    anios = anios_experiencia(intervalos)
    detalle = f"{anios:.1f} años en cargos relacionados (mínimo {c.anios_min:g})".replace(".", ",")
    if anios >= c.anios_min:
        return _res(c, "cumple", detalle, citas)
    if anios >= c.anios_min / 2 and anios > 0:
        return _res(c, "parcial", detalle, citas)
    return _res(c, "no_identificado", detalle, citas)


def _formacion(c: Criterio, ext, ver) -> ResultadoCriterio:
    req = ORDEN_FORMACION[c.nivel_min]
    rango = {"cumple": 2, "parcial": 1}
    mejor = None  # (estado, formación, nivel, nota)
    for f in _verificados(ext, ver, "formacion"):
        nivel = nivel_formacion(f)
        n = ORDEN_FORMACION[nivel]
        area = _coincide([f.titulo, f.cita], c.palabras_clave)
        if n >= req and area:
            estado, nota = "cumple", ""
        elif n >= req:
            estado, nota = "parcial", "otra área"
        elif area and n == req - 1:
            estado, nota = "parcial", "un nivel por debajo"
        else:
            continue
        if en_curso(f):
            estado, nota = "parcial", "carrera en curso, sin título"
        if mejor is None or rango[estado] > rango[mejor[0]]:
            mejor = (estado, f, nivel, nota)
    if mejor is None:
        return _res(c, "no_identificado",
                    f"No se encontró formación verificada de {NOMBRE_NIVEL[c.nivel_min]} en el área")
    estado, f, nivel, nota = mejor
    detalle = f"{f.titulo} ({NOMBRE_NIVEL[nivel]})" + (f": {nota}" if nota else "")
    return _res(c, estado, detalle, [f.cita])


def _idioma(c: Criterio, ext, ver) -> ResultadoCriterio:
    req = ORDEN_IDIOMA[c.nivel_idioma]
    nombres = [c.idioma, *c.palabras_clave]  # p. ej. "inglés", "english"
    hallados = [i for i in _verificados(ext, ver, "idiomas") if _coincide([i.idioma, i.cita], nombres)]
    if not hallados:
        return _res(c, "no_identificado", f"No se encontró {c.idioma} con evidencia verificada")
    i = max(hallados, key=lambda x: ORDEN_IDIOMA[x.nivel])
    nivel = ORDEN_IDIOMA[i.nivel]
    estado = "cumple" if nivel >= req else "parcial" if nivel == req - 1 else "no_identificado"
    return _res(c, estado, f"{c.idioma}: nivel {i.nivel} (requerido {c.nivel_idioma})", [i.cita])


def _res(c: Criterio, estado: str, detalle: str, citas: list[str] | None = None) -> ResultadoCriterio:
    return ResultadoCriterio(criterio_id=c.id, nombre=c.nombre, peso=c.peso, estado=estado,
                             detalle=detalle, citas=citas or [])


# ---------------------------------------------------------------- API
def evaluar_criterios(vac: Vacante, ext: ExtraccionCV, ver: dict[str, list[bool]],
                      hoy: date | None = None) -> list[ResultadoCriterio]:
    hoy = hoy or date.today()
    out = []
    for c in vac.criterios:
        if c.tipo == "habilidad":
            out.append(_habilidad(c, ext, ver))
        elif c.tipo == "experiencia":
            out.append(_experiencia(c, ext, ver, hoy))
        elif c.tipo == "formacion":
            out.append(_formacion(c, ext, ver))
        else:
            out.append(_idioma(c, ext, ver))
    return out


def puntaje(resultados: list[ResultadoCriterio]) -> float:
    """Σ wᵢ · sᵢ  (los pesos suman 100, así que el puntaje va de 0 a 100)."""
    return round(sum(r.peso * r.s for r in resultados), 1)
