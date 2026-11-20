"""Normalización de texto compartida (comparar citas y palabras clave)."""
from __future__ import annotations

import re
import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, sin guiones de corte de línea y con espacios simples."""
    t = texto.replace("­", "")  # guion suave
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)  # palabra cortada al final de línea
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = re.sub(r"[“”\"'«»`´]", "", t)
    t = re.sub(r"[•·▪●•]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def contiene_palabra(texto_norm: str, palabra: str) -> bool:
    """¿El texto (ya normalizado) contiene la palabra o frase completa?"""
    p = normalizar(palabra)
    if not p:
        return False
    return re.search(r"(?<![a-z0-9])" + re.escape(p) + r"(?![a-z0-9])", texto_norm) is not None
