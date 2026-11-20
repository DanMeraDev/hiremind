# HireMind · agente local de preselección de hojas de vida

Prototipo del proyecto de Inteligencia Artificial (EPN). El agente lee hojas de vida en PDF, las compara con los criterios de una vacante y entrega un **ranking justificado con evidencias**. Todo corre en el equipo de la PYME: los CV no salen a internet.

**La IA no contrata ni descarta a nadie.** Ordena todos los CV y una persona revisa el top 5.

## Cómo funciona

| Paso | Quién | Qué hace | Archivo |
|---|---|---|---|
| 1 | Python | Lee el PDF con PyMuPDF. Si no tiene texto (escaneado), va a **revisión manual** | `agente/ingesta.py` |
| 5 | Python | Quita del texto edad, estado civil, nacionalidad, etc. **antes** de enviarlo al modelo | `agente/equidad.py` |
| 2 | LLM | Extrae formación, experiencia, habilidades, idiomas y proyectos a JSON, **con una cita textual** por dato | `agente/llm.py` |
| 3 | Python | Valida el JSON; si falla, reintenta con el error (máx. 2), luego revisión manual | `agente/llm.py` |
| 4 | Python | Verifica que cada cita exista en el CV. Sin cita → "no verificado", vale 0 | `agente/evidencia.py` |
| 6 | Python | Compara con la vacante: cumple (1) · parcial (0,5) · no identificado (0). **Puntaje = Σ wᵢ·sᵢ** | `agente/puntuacion.py` |
| 7 | LLM | Redacta la justificación usando **solo** evidencias verificadas | `agente/llm.py` |
| 8 | Python | Guarda en SQLite; la persona puede corregir un criterio y el puntaje se recalcula | `agente/db.py` |

El orden de los pasos está en `agente/pipeline.py`.

## Requisitos

- PC con 16 GB de RAM (con GPU es más rápido, pero no es obligatoria)
- [LM Studio](https://lmstudio.ai) con el modelo **Qwen3-4B-Instruct-2507** (GGUF, Q4_K_M)
- Python 3.12

## Instalación

```bash
# 1. Modelo y servidor local
lms get qwen/qwen3-4b-2507@q4_k_m
lms load qwen/qwen3-4b-2507 --context-length 8192 -y
lms server start            # http://localhost:1234/v1

# 2. Aplicación
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

En la pantalla **1 · Vacante** hay un botón para cargar 2 vacantes de ejemplo.

## Datos de prueba

`datos/cvs/` tiene 15 hojas de vida **ficticias** (`scripts/generar_cvs.py`):

- CV 01 a 08 → vacante "Asistente contable"; CV 09 a 15 → "Desarrollador/a junior Python"
- `cv_08_escaneado.pdf`: solo imagen → debe ir a revisión manual
- `cv_13_trampa_disenador.pdf`: diseñador sin programación → el agente no debe inventarle Python
- Varios CV traen edad, estado civil o nacionalidad → deben excluirse antes del análisis

## Pruebas

```bash
.venv/bin/python -m pytest              # reglas, equidad, evidencias y SQLite (sin LM Studio)
.venv/bin/python scripts/probar_lote.py # punta a punta con LM Studio: ranking y tiempos por CV
```

## Configuración

Variables de entorno (ver `agente/config.py`): `HIREMIND_LLM_URL`, `HIREMIND_MODELO`, `HIREMIND_DB`.
Para usar otro modelo (por ejemplo uno de 7B) basta con cargarlo en LM Studio y cambiar `HIREMIND_MODELO`.
