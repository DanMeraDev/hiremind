"""Paso 1: leer el PDF con PyMuPDF y decidir si el texto es legible."""
from __future__ import annotations

from dataclasses import dataclass

import pymupdf

from . import config


@dataclass
class Documento:
    texto: str
    paginas: int
    legible: bool
    motivo: str = ""


def leer_pdf(datos: bytes) -> Documento:
    try:
        with pymupdf.open(stream=datos, filetype="pdf") as doc:
            paginas = doc.page_count
            texto = "\n".join(p.get_text("text") for p in doc)
    except Exception as e:  # archivo dañado o que no es PDF
        return Documento("", 0, False, f"No se pudo abrir el PDF ({type(e).__name__})")

    utiles = len("".join(texto.split()))
    if utiles < config.MIN_CARACTERES:
        return Documento(texto, paginas, False,
                         "PDF escaneado o sin texto extraíble: requiere revisión manual")
    return Documento(texto, paginas, True)
