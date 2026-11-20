"""Cliente del LLM local (LM Studio). Pasos 2-3 (extraer + validar) y 7 (justificar).

El modelo solo extrae datos con su cita y redacta la justificación.
No asigna puntajes.
"""
from __future__ import annotations

import json

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from . import config
from .modelos import ExtraccionCV, ResultadoCriterio, esquema_json_estricto

PROMPT_EXTRACCION = """Eres un asistente que extrae datos de hojas de vida (CV) en español.
Devuelve SOLO un JSON que cumpla el esquema. Reglas:
- Extrae únicamente lo que está escrito en el CV. Si algo no aparece, deja la lista vacía. No inventes.
- En cada elemento, "cita" debe ser una frase COPIADA TEXTUALMENTE del CV (máximo 25 palabras) que respalde el dato.
- Fechas de experiencia en formato AAAA-MM (o AAAA si no hay mes). Si el trabajo sigue vigente, fin = "actual".
- nivel de formación: bachillerato, tecnico, tecnologo, tercer_nivel (licenciatura/ingeniería), cuarto_nivel (maestría/doctorado) u otro (cursos).
- nivel de idioma: basico (A1-A2), intermedio (B1-B2), avanzado (C1-C2) o nativo.
- habilidades: herramientas, programas, conocimientos técnicos y habilidades blandas mencionadas explícitamente.
- NO extraigas edad, fecha de nacimiento, estado civil, género, nacionalidad, religión, foto ni datos de contacto."""

PROMPT_JUSTIFICACION = """Eres un asistente de selección de personal. Redacta en español una justificación breve
(3 a 5 oraciones) del resultado de un candidato para la vacante indicada.
Reglas:
- Usa SOLO la información de los criterios y evidencias que se te entregan. No agregues nada más.
- Menciona primero las fortalezas y luego lo que no se pudo identificar en el CV.
- No menciones edad, género, estado civil, nacionalidad, religión, apariencia ni otros datos personales.
- No digas si se debe contratar o no: la decisión es de la persona que revisa.
Devuelve un JSON con el campo "justificacion"."""


class _Justificacion(BaseModel):
    justificacion: str


class ErrorExtraccion(Exception):
    """El modelo no produjo un JSON válido tras los reintentos."""

    def __init__(self, mensaje: str, intentos: int):
        super().__init__(mensaje)
        self.intentos = intentos


def _cliente() -> OpenAI:
    return OpenAI(base_url=config.LLM_URL, api_key="lm-studio", timeout=180)


def servidor_disponible() -> tuple[bool, str]:
    """¿Responde LM Studio y está cargado el modelo configurado?"""
    try:
        ids = [m.id for m in _cliente().with_options(timeout=5).models.list().data]
    except Exception as e:
        return False, f"LM Studio no responde en {config.LLM_URL} ({type(e).__name__})"
    if config.MODELO not in ids:
        return False, f"El modelo {config.MODELO} no está cargado (disponibles: {', '.join(ids) or 'ninguno'})"
    return True, config.MODELO


def _formato(nombre: str, modelo: type[BaseModel]) -> dict:
    return {"type": "json_schema",
            "json_schema": {"name": nombre, "strict": True, "schema": esquema_json_estricto(modelo)}}


def extraer(texto_cv: str) -> tuple[ExtraccionCV, int]:
    """Extrae el CV a JSON. Si falla la validación, reintenta con el error (máx. MAX_REINTENTOS).

    Devuelve (extracción, número de intentos). Lanza ErrorExtraccion si no lo logra."""
    cliente = _cliente()
    mensajes = [
        {"role": "system", "content": PROMPT_EXTRACCION},
        {"role": "user", "content": "CV:\n\"\"\"\n" + texto_cv[: config.MAX_CHARS_CV] + "\n\"\"\""},
    ]
    ultimo_error = ""
    for intento in range(1, config.MAX_REINTENTOS + 2):
        resp = cliente.chat.completions.create(
            model=config.MODELO, messages=mensajes, temperature=0, max_tokens=3000,
            response_format=_formato("extraccion_cv", ExtraccionCV),
        )
        contenido = resp.choices[0].message.content or ""
        try:
            return ExtraccionCV.model_validate(json.loads(contenido)), intento
        except (json.JSONDecodeError, ValidationError) as e:
            ultimo_error = str(e)[:800]
            mensajes += [
                {"role": "assistant", "content": contenido[:4000]},
                {"role": "user", "content": f"El JSON no es válido: {ultimo_error}\nCorrígelo y devuelve el JSON completo."},
            ]
    raise ErrorExtraccion(f"JSON inválido tras {config.MAX_REINTENTOS} reintentos: {ultimo_error}",
                          config.MAX_REINTENTOS + 1)


def justificar(titulo_vacante: str, resultados: list[ResultadoCriterio]) -> str:
    """Redacta la justificación usando solo las evidencias verificadas."""
    datos = [{"criterio": r.nombre, "peso": r.peso, "resultado": r.estado.replace("_", " "),
              "detalle": r.detalle, "evidencias": r.citas[:3]} for r in resultados]
    resp = _cliente().chat.completions.create(
        model=config.MODELO, temperature=0.2, max_tokens=500,
        response_format=_formato("justificacion", _Justificacion),
        messages=[
            {"role": "system", "content": PROMPT_JUSTIFICACION},
            {"role": "user", "content": f"Vacante: {titulo_vacante}\nCriterios evaluados:\n"
                                        + json.dumps(datos, ensure_ascii=False, indent=1)},
        ],
    )
    return _Justificacion.model_validate_json(resp.choices[0].message.content or "").justificacion.strip()
