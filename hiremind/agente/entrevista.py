"""Preguntas sugeridas para entrevistar a la persona seleccionada.

Se generan con el LLM local a partir de la vacante, los criterios evaluados y la
evidencia verificada del CV (nunca con datos personales). Si el modelo no
responde, se arman con una plantilla basada en los criterios.
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field

from . import equidad, llm
from .modelos import ResultadoCriterio, Vacante

TipoPregunta = Literal["tecnica", "experiencia", "situacional", "verificacion"]


class Pregunta(BaseModel):
    pregunta: str
    criterio: str = Field(description="Nombre del criterio de la vacante al que apunta, o 'General'")
    tipo: TipoPregunta
    proposito: str = Field(description="Qué se busca confirmar con la pregunta (una frase)")


class _Preguntas(BaseModel):
    preguntas: list[Pregunta]


PROMPT = """Eres un especialista en selección de personal. Prepara preguntas para la entrevista de una
persona candidata que fue seleccionada para el puesto indicado. Escribe en español.
Reglas:
- Entre 6 y 8 preguntas, concretas y abiertas.
- Usa la evidencia del CV: pregunta por proyectos, cargos y herramientas que la persona menciona.
- Para cada criterio "parcial" o "no identificado" incluye al menos una pregunta de verificación
  (el CV puede no mostrarlo, pero la persona quizá sí lo tiene).
- Incluye al menos una pregunta situacional ligada a las tareas del puesto.
- Prohibido preguntar por edad, estado civil, hijos, embarazo, género, religión, nacionalidad,
  etnia, salud, apariencia u otros datos personales.
- tipo: tecnica, experiencia, situacional o verificacion.
Devuelve un JSON con el campo "preguntas"."""


def _contexto(vac: Vacante, criterios: list[ResultadoCriterio], extraccion: dict) -> dict:
    verif = lambda x: x.get("verificado", True)  # noqa: E731
    return {
        "puesto": vac.titulo,
        "descripcion": vac.descripcion,
        "criterios": [{"criterio": r.nombre, "peso": r.peso, "resultado": r.estado.replace("_", " "),
                       "detalle": r.detalle, "evidencias": r.citas[:2]} for r in criterios],
        "experiencia": [f"{x['cargo']} · {x.get('empresa', '')} ({x['inicio']} – {x['fin']})"
                        for x in extraccion.get("experiencia", []) if verif(x)][:6],
        "proyectos": [x["nombre"] for x in extraccion.get("proyectos", []) if verif(x)][:5],
        "habilidades": [x["nombre"] for x in extraccion.get("habilidades", []) if verif(x)][:15],
    }


_CUMPLE = {
    "habilidad": "Cuéntenos un caso concreto en el que usó «{n}». ¿Qué hizo usted y qué resultado obtuvo?",
    "experiencia": "Describa sus responsabilidades principales en relación con «{n}». ¿De qué logro se siente más orgulloso/a?",
    "formacion": "De su formación en «{n}», ¿qué conocimientos aplica con más frecuencia en el trabajo?",
    "idioma": "¿En qué situaciones laborales ha usado {n}? Cuéntenos un ejemplo.",
}
_FALTA = {
    "habilidad": "En el CV no encontramos evidencia clara de «{n}». ¿La ha usado? Descríbanos un ejemplo.",
    "experiencia": "En el CV no se ve con claridad «{n}». ¿Ha trabajado en esto? Cuéntenos dónde y durante cuánto tiempo.",
    "formacion": "En el CV no encontramos «{n}». ¿Qué estudios o cursos tiene en esta área?",
    "idioma": "En el CV no encontramos evidencia de «{n}». ¿Cuál es su nivel real y cómo lo ha practicado?",
}
_PARCIAL = "El CV muestra «{n}» solo en parte. ¿Qué experiencia adicional tiene que no aparezca en el documento?"


def plantilla(vac: Vacante, criterios: list[ResultadoCriterio], extraccion: dict) -> list[Pregunta]:
    """Respaldo sin LLM: una pregunta por criterio según su resultado + una situacional."""
    tipos = {c.id: c.tipo for c in vac.criterios}
    out = []
    for r in sorted(criterios, key=lambda r: -r.peso):
        tipo = tipos.get(r.criterio_id, "habilidad")
        if r.estado == "cumple":
            out.append(Pregunta(pregunta=_CUMPLE[tipo].format(n=r.nombre), criterio=r.nombre,
                                tipo="tecnica" if tipo == "habilidad" else "experiencia",
                                proposito="Profundizar en la evidencia que aparece en el CV"))
        else:
            plantilla_txt = _PARCIAL if r.estado == "parcial" else _FALTA[tipo]
            out.append(Pregunta(pregunta=plantilla_txt.format(n=r.nombre), criterio=r.nombre, tipo="verificacion",
                                proposito="Confirmar un criterio que el CV no muestra por completo"))
    exp = [x for x in extraccion.get("experiencia", []) if x.get("verificado", True)]
    if exp:
        out.append(Pregunta(pregunta=f"En su cargo de {exp[0]['cargo']}, ¿cuál fue el mayor reto que enfrentó "
                                     "y cómo lo resolvió?", criterio="General", tipo="experiencia",
                            proposito="Conocer su forma de resolver problemas en un contexto real"))
    out.append(Pregunta(pregunta=f"Imagine su primera semana como {vac.titulo.split('·')[0].strip()}. "
                                 "¿Qué priorizaría y por qué?", criterio="General", tipo="situacional",
                        proposito="Ver cómo entiende las tareas del puesto"))
    return out[:8]


def sugerir(vac: Vacante, criterios: list[ResultadoCriterio], extraccion: dict) -> tuple[list[Pregunta], str]:
    """Devuelve (preguntas, origen) con origen 'llm' o 'plantilla'."""
    try:
        resp = llm._cliente().chat.completions.create(
            model=llm.config.MODELO, temperature=0.4, max_tokens=1500,
            response_format=llm._formato("preguntas_entrevista", _Preguntas),
            messages=[{"role": "system", "content": PROMPT},
                      {"role": "user", "content": json.dumps(_contexto(vac, criterios, extraccion),
                                                             ensure_ascii=False, indent=1)}],
        )
        preguntas = _Preguntas.model_validate_json(resp.choices[0].message.content or "").preguntas
        # filtro de equidad: se descarta cualquier pregunta que toque datos personales
        preguntas = [p for p in preguntas if p.pregunta.strip() and not equidad.terminos_sensibles(p.pregunta)]
        if len(preguntas) >= 3:
            return preguntas[:8], "llm"
    except Exception:
        pass
    return plantilla(vac, criterios, extraccion), "plantilla"
