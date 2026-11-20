"""Paso 4: verificar que cada cita del LLM exista realmente en el CV.

Un dato sin cita verificable no cuenta para el puntaje ("no verificado", vale 0).
"""
from __future__ import annotations

from rapidfuzz import fuzz

from . import config
from .modelos import ExtraccionCV
from .texto import normalizar

# Las citas cortas deben aparecer exactas; las largas toleran pequeñas diferencias
# (saltos de línea, viñetas o tildes que el PDF parte de forma distinta).
_LARGO_MIN_DIFUSO = 25


def cita_valida(cita: str, texto_norm: str) -> bool:
    c = normalizar(cita)
    if len(c) < 3:
        return False
    if c in texto_norm:
        return True
    if len(c) >= _LARGO_MIN_DIFUSO:
        return fuzz.partial_ratio(c, texto_norm) >= config.UMBRAL_CITA
    return False


def verificar(ext: ExtraccionCV, texto_cv: str) -> dict[str, list[bool]]:
    """Devuelve, por sección, una lista paralela con True/False por cada elemento."""
    texto_norm = normalizar(texto_cv)
    return {
        seccion: [cita_valida(item.cita, texto_norm) for item in getattr(ext, seccion)]
        for seccion in ("formacion", "experiencia", "habilidades", "idiomas", "proyectos")
    }
