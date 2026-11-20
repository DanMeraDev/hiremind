"""Paso 5: filtro de equidad.

Tres capas:
1. Antes del LLM se quitan del texto las líneas con datos personales sensibles
   (edad, estado civil, nacionalidad...), así el modelo nunca los ve.
2. El esquema JSON no tiene campos para esos datos (ver modelos.esquema_json_estricto).
3. Los criterios de la vacante y la justificación no pueden mencionarlos.
"""
from __future__ import annotations

import re

from .texto import normalizar

_ETIQUETAS = [
    "fecha de nacimiento", "lugar de nacimiento", "nacimiento", "edad", "estado civil",
    "nacionalidad", "sexo", "genero", "religion", "etnia", "raza", "cedula",
    "cedula de identidad", "numero de hijos", "hijos", "discapacidad", "foto", "fotografia",
]
_LINEA_SENSIBLE = re.compile(
    r"^\s*(?:" + "|".join(re.escape(e) for e in sorted(_ETIQUETAS, key=len, reverse=True)) + r")\s*[:\-]"
)

TERMINOS_SENSIBLES = [
    "edad", "anos de edad", "joven", "nacimiento", "estado civil",
    "casado", "casada", "soltero", "soltera", "divorciado", "divorciada", "hijos", "embarazo",
    "embarazada", "sexo", "genero", "hombre", "mujer", "masculino", "femenino", "religion",
    "catolico", "catolica", "cristiano", "cristiana", "evangelico", "evangelica",
    "nacionalidad", "extranjero", "extranjera", "etnia", "raza", "indigena", "afro",
    "discapacidad", "apariencia", "buena presencia",
]
_TERMINO = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in TERMINOS_SENSIBLES) + r")\b")


def limpiar_texto(texto: str) -> tuple[str, list[str]]:
    """Quita las líneas con datos sensibles. Devuelve (texto limpio, etiquetas quitadas)."""
    quitadas, lineas = [], []
    for linea in texto.splitlines():
        m = _LINEA_SENSIBLE.match(normalizar(linea))
        if m:
            quitadas.append(m.group(0).rstrip(":- ").strip())
        else:
            lineas.append(linea)
    return "\n".join(lineas), quitadas


def terminos_sensibles(texto: str) -> list[str]:
    """Términos sensibles que aparecen en un texto (criterio o justificación)."""
    return sorted(set(_TERMINO.findall(normalizar(texto))))
