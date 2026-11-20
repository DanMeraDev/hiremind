"""Flujo de razonamiento completo para una hoja de vida (pasos 1 a 8)."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from . import db, equidad, evidencia, llm, puntuacion
from .ingesta import leer_pdf
from .modelos import ResultadoCriterio, Vacante


@dataclass
class Resultado:
    archivo: str
    estado: str  # 'evaluado' | 'revision_manual'
    motivo: str = ""
    nombre: str = ""
    puntaje: float = 0.0
    justificacion: str = ""
    segundos: float = 0.0
    intentos: int = 0
    criterios: list[ResultadoCriterio] = field(default_factory=list)
    no_verificados: int = 0
    datos_quitados: list[str] = field(default_factory=list)


def justificacion_plantilla(resultados: list[ResultadoCriterio]) -> str:
    """Respaldo sin LLM: frase armada solo con los resultados verificados."""
    fuertes = [r.nombre for r in resultados if r.estado == "cumple"]
    parciales = [r.nombre for r in resultados if r.estado == "parcial"]
    faltan = [r.nombre for r in resultados if r.estado == "no_identificado"]
    partes = []
    if fuertes:
        partes.append("Cumple con: " + ", ".join(fuertes) + ".")
    if parciales:
        partes.append("Cumple parcialmente: " + ", ".join(parciales) + ".")
    if faltan:
        partes.append("No se identificó evidencia en el CV para: " + ", ".join(faltan) + ".")
    return " ".join(partes)


def evaluar_cv(con, vac: Vacante, archivo: str, datos: bytes) -> Resultado:
    t0 = time.perf_counter()

    # 1. Leer documento
    doc = leer_pdf(datos)
    if not doc.legible:
        db.guardar_revision_manual(con, vac.id, archivo, doc.motivo)
        return Resultado(archivo, "revision_manual", doc.motivo, segundos=time.perf_counter() - t0)

    # 5 (antes del LLM). Excluir datos personales: el modelo nunca los ve
    texto, quitados = equidad.limpiar_texto(doc.texto)

    # 2-3. Extraer a JSON y validar (con reintentos)
    try:
        ext, intentos = llm.extraer(texto)
    except llm.ErrorExtraccion as e:
        motivo = f"El modelo no devolvió un JSON válido ({e.intentos} intentos)"
        db.guardar_revision_manual(con, vac.id, archivo, motivo)
        return Resultado(archivo, "revision_manual", motivo, intentos=e.intentos,
                         segundos=time.perf_counter() - t0)

    # 4. Verificar evidencia: cada cita debe existir en el CV
    ver = evidencia.verificar(ext, texto)
    no_verificados = sum(not ok for lista in ver.values() for ok in lista)

    # 6. Comparar y puntuar (Python, Σ wᵢ·sᵢ)
    resultados = puntuacion.evaluar_criterios(vac, ext, ver)
    total = puntuacion.puntaje(resultados)

    # 7. Redactar justificación solo con evidencias verificadas
    try:
        justificacion = llm.justificar(vac.titulo, resultados)
        if equidad.terminos_sensibles(justificacion) or not justificacion:
            justificacion = justificacion_plantilla(resultados)
    except Exception:
        justificacion = justificacion_plantilla(resultados)

    # 8. Guardar resultado
    segundos = time.perf_counter() - t0
    extraccion = ext.model_dump()
    for seccion, oks in ver.items():  # guardar también qué se verificó
        for item, ok in zip(extraccion[seccion], oks):
            item["verificado"] = ok
    db.guardar_evaluacion(con, vac.id, archivo, ext.nombre_candidato, quitados, total, justificacion,
                          extraccion, segundos, intentos, resultados)
    return Resultado(archivo, "evaluado", nombre=ext.nombre_candidato, puntaje=total,
                     justificacion=justificacion, segundos=segundos, intentos=intentos,
                     criterios=resultados, no_verificados=no_verificados, datos_quitados=quitados)
