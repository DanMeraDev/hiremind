"""Pruebas de las partes deterministas (no necesitan LM Studio)."""
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from agente import db, equidad, evidencia, puntuacion
from agente.ingesta import leer_pdf
from agente.modelos import Criterio, ExtraccionCV, Vacante, esquema_json_estricto
from agente.texto import normalizar

CVS = Path(__file__).resolve().parent.parent / "datos" / "cvs"
HOY = date(2026, 11, 20)

TEXTO = """Ana Pérez
Fecha de nacimiento: 01/01/1990
Estado civil: Soltera
Asistente contable, Comercial Los Andes (2021-02 a la actualidad): facturación electró-
nica y declaraciones en el SRI.
Habilidades: Excel avanzado (tablas dinámicas)
Ingeniería en Contabilidad y Auditoría, Universidad Central (2014-2019)
Inglés intermedio (B1)"""


def ext(**kw) -> ExtraccionCV:
    base = dict(nombre_candidato="Ana Pérez", formacion=[], experiencia=[], habilidades=[], idiomas=[], proyectos=[])
    base.update(kw)
    return ExtraccionCV.model_validate(base)


VAC = Vacante(titulo="Asistente contable", criterios=[
    Criterio(id="exp", tipo="experiencia", nombre="Experiencia contable", peso=40, anios_min=2,
             palabras_clave=["contable"]),
    Criterio(id="excel", tipo="habilidad", nombre="Excel", peso=30, palabras_clave=["excel"]),
    Criterio(id="form", tipo="formacion", nombre="Contabilidad", peso=20, nivel_min="tercer_nivel",
             palabras_clave=["contabilidad"]),
    Criterio(id="en", tipo="idioma", nombre="Inglés", peso=10, idioma="ingles", nivel_idioma="avanzado"),
])


# ---------------------------------------------------------------- equidad
def test_limpiar_texto_quita_datos_sensibles():
    limpio, quitadas = equidad.limpiar_texto(TEXTO)
    assert "nacimiento" not in limpio.lower() and "soltera" not in limpio.lower()
    assert quitadas == ["fecha de nacimiento", "estado civil"]
    assert "Excel avanzado" in limpio


def test_criterio_discriminatorio_se_rechaza():
    with pytest.raises(ValidationError, match="datos personales"):
        Vacante(titulo="x", criterios=[Criterio(id="a", tipo="habilidad", nombre="Mujer menor de 30 años",
                                                peso=100, palabras_clave=["excel"])])


def test_pesos_deben_sumar_100():
    with pytest.raises(ValidationError, match="sumar 100"):
        Vacante(titulo="x", criterios=[Criterio(id="a", tipo="habilidad", nombre="Excel", peso=60,
                                                palabras_clave=["excel"])])


def test_esquema_no_permite_campos_extra():
    esquema = esquema_json_estricto(ExtraccionCV)
    assert esquema["additionalProperties"] is False
    assert "edad" not in str(esquema)


# ---------------------------------------------------------------- evidencia
def test_cita_exacta_y_con_corte_de_linea():
    t = normalizar(TEXTO)
    assert evidencia.cita_valida("Excel avanzado (tablas dinámicas)", t)
    assert evidencia.cita_valida("facturación electrónica y declaraciones en el SRI", t)  # palabra partida


def test_cita_inventada_no_se_acepta():
    t = normalizar(TEXTO)
    assert not evidencia.cita_valida("Python avanzado", t)
    assert not evidencia.cita_valida("Experiencia de 5 años como contador general en un banco", t)


def test_dato_no_verificado_vale_cero():
    e = ext(habilidades=[{"nombre": "Python", "cita": "Python avanzado"}])  # cita inventada
    ver = evidencia.verificar(e, TEXTO)
    r = puntuacion.evaluar_criterios(
        Vacante(titulo="x", criterios=[Criterio(id="py", tipo="habilidad", nombre="Python", peso=100,
                                                palabras_clave=["python"])]), e, ver, HOY)
    assert ver["habilidades"] == [False]
    assert r[0].estado == "no_identificado" and puntuacion.puntaje(r) == 0


# ---------------------------------------------------------------- puntuación
def test_puntaje_ponderado():
    e = ext(
        experiencia=[{"cargo": "Asistente contable", "empresa": "Comercial Los Andes", "inicio": "2021-02",
                      "fin": "actual", "descripcion": "", "cita": "Asistente contable, Comercial Los Andes"}],
        habilidades=[{"nombre": "Excel", "cita": "Excel avanzado (tablas dinámicas)"}],
        formacion=[{"titulo": "Ingeniería en Contabilidad y Auditoría", "institucion": "Universidad Central",
                    "nivel": "tercer_nivel", "cita": "Ingeniería en Contabilidad y Auditoría"}],
        idiomas=[{"idioma": "Inglés", "nivel": "intermedio", "cita": "Inglés intermedio (B1)"}],
    )
    r = puntuacion.evaluar_criterios(VAC, e, evidencia.verificar(e, TEXTO), HOY)
    estados = {x.criterio_id: x.estado for x in r}
    assert estados == {"exp": "cumple", "excel": "cumple", "form": "cumple", "en": "parcial"}
    assert puntuacion.puntaje(r) == 40 + 30 + 20 + 5  # Σ wᵢ·sᵢ


def test_experiencia_solapada_no_se_cuenta_dos_veces():
    m = lambda a, b: a * 12 + b - 1
    assert puntuacion.anios_experiencia([(m(2020, 1), m(2021, 12)), (m(2021, 1), m(2022, 12))]) == 3.0


def test_experiencia_parcial():
    e = ext(experiencia=[{"cargo": "Asistente contable", "empresa": "", "inicio": "2025-11", "fin": "actual",
                          "descripcion": "", "cita": "Asistente contable"}])
    r = puntuacion.evaluar_criterios(VAC, e, evidencia.verificar(e, TEXTO), HOY)
    assert r[0].estado == "parcial"  # 1 año de 2 requeridos


# ---------------------------------------------------------------- ingesta y base de datos
def test_pdf_escaneado_va_a_revision_manual():
    doc = leer_pdf((CVS / "cv_08_escaneado.pdf").read_bytes())
    assert not doc.legible and "revisión manual" in doc.motivo


def test_pdf_digital_es_legible():
    doc = leer_pdf((CVS / "cv_01_contable.pdf").read_bytes())
    assert doc.legible and "Andrea Salazar" in doc.texto


def test_archivo_que_no_es_pdf():
    assert not leer_pdf(b"no soy un pdf").legible


def test_correccion_humana_recalcula(tmp_path):
    e = ext(habilidades=[{"nombre": "Excel", "cita": "Excel avanzado (tablas dinámicas)"}])
    r = puntuacion.evaluar_criterios(VAC, e, evidencia.verificar(e, TEXTO), HOY)
    with db.conectar(str(tmp_path / "t.db")) as con:
        vid = db.guardar_vacante(con, VAC)
        db.guardar_evaluacion(con, vid, "a.pdf", "Ana", [], puntuacion.puntaje(r), "j", e.model_dump(), 1.0, 1, r)
        fila = db.ranking(con, vid)[0]
        assert fila["puntaje"] == 30
        nuevo = db.corregir_criterio(con, fila["eval_id"], "exp", "cumple")
        assert nuevo == 70 and db.ranking(con, vid)[0]["corregida"] == 1


# ---------------------------------------------------------------- casos encontrados con el modelo real
TEXTO2 = """Ingeniería en Contabilidad y Auditoría CPA, Universidad Central (2014-2019).
Cursando octavo semestre de Ingeniería en Sistemas, Escuela Politécnica Nacional.
Curso de Python básico (40 horas), Fundación Código Ecuador (2024).
Bot de inventario: script en Python que lee hojas de Excel y envía alertas de stock.
Habilidades: PHP, MySQL"""

PY = Vacante(titulo="x", criterios=[Criterio(id="py", tipo="habilidad", nombre="Python", peso=100,
                                             palabras_clave=["python"])])
SIS = Vacante(titulo="x", criterios=[Criterio(id="f", tipo="formacion", nombre="Sistemas", peso=100,
                                              nivel_min="tecnologo", palabras_clave=["sistemas"])])


def _form(titulo, cita, nivel):
    return {"titulo": titulo, "institucion": "", "nivel": nivel, "cita": cita}


def _eval(vac, e, texto=TEXTO2):
    return puntuacion.evaluar_criterios(vac, e, evidencia.verificar(e, texto), HOY)[0]


def test_nivel_se_deduce_del_titulo_no_del_modelo():
    # el modelo dijo "tecnologo" pero es una ingeniería -> tercer nivel
    e = ext(formacion=[_form("Ingeniería en Contabilidad y Auditoría CPA",
                             "Ingeniería en Contabilidad y Auditoría CPA, Universidad Central (2014-2019).", "tecnologo")])
    assert _eval(VAC.model_copy(update={"criterios": [VAC.criterios[2].model_copy(update={"peso": 100})]}), e).estado == "cumple"


def test_carrera_en_curso_es_parcial():
    e = ext(formacion=[_form("Ingeniería en Sistemas",
                             "Cursando octavo semestre de Ingeniería en Sistemas, Escuela Politécnica Nacional.", "cuarto_nivel")])
    r = _eval(SIS, e)
    assert r.estado == "parcial" and "en curso" in r.detalle


def test_habilidad_copiada_de_un_proyecto_es_parcial():
    cita = "script en Python que lee hojas de Excel y envía alertas de stock."
    e = ext(habilidades=[{"nombre": "Python", "cita": cita}],
            proyectos=[{"nombre": "Bot de inventario", "descripcion": "",
                        "cita": "Bot de inventario: script en Python que lee hojas de Excel y envía alertas de stock."}])
    assert _eval(PY, e).estado == "parcial"


def test_habilidad_en_un_curso_es_parcial():
    e = ext(formacion=[_form("Curso de Python básico",
                             "Curso de Python básico (40 horas), Fundación Código Ecuador (2024).", "otro")])
    assert _eval(PY, e).estado == "parcial"


def test_habilidad_listada_sigue_cumpliendo_aunque_tambien_este_en_proyecto():
    e = ext(habilidades=[{"nombre": "Python", "cita": "Python"}],
            proyectos=[{"nombre": "Bot", "descripcion": "", "cita": "script en Python que lee hojas de Excel"}])
    assert _eval(PY, e).estado == "cumple"


def test_fechas_se_toman_de_la_cita():
    cita = "Asistente contable, Importadora del Sur (2025-05 a la actualidad): registro de facturas."
    assert puntuacion.fechas_de_cita(cita, "actual", "actual") == ("2025-05", "actual")
    assert puntuacion.fechas_de_cita("Vendedor (2019-01 a 2025-04)", "x", "y") == ("2019-01", "2025-04")
    assert puntuacion.fechas_de_cita("Vendedor en Tía", "2020-01", "2021-01") == ("2020-01", "2021-01")
