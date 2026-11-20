# HireMind · agente local de preselección de hojas de vida

Prototipo del proyecto de Inteligencia Artificial (EPN). El agente lee hojas de vida en PDF, las compara con los criterios de una vacante y entrega un **ranking justificado con evidencias**. Todo corre en el equipo de la PYME: los CV no salen a internet.

**La IA no contrata ni descarta a nadie.** Ordena todos los CV y una persona revisa el top 5.

## Arquitectura

```
Navegador ──► React (web/)  ──HTTP /api──►  FastAPI (api/)  ──►  agente/ (Python)
                                                                   │  ├─ PyMuPDF      lee el PDF
                                                                   │  ├─ OpenAI SDK ─► LM Studio · Qwen3-4B  (localhost:1234)
                                                                   │  └─ reglas       verifica citas y puntúa
                                                                   └─► SQLite (hiremind.db) + copia de los PDF (archivos/)
```

| Capa | Tecnología | Carpeta |
|---|---|---|
| Interfaz | React 19 · TypeScript · Vite · Tailwind CSS · React Router · TanStack Query | `web/` |
| API | FastAPI · uvicorn | `api/main.py` |
| Agente | Python 3.12 · Pydantic · PyMuPDF · rapidfuzz | `agente/` |
| Modelo | LM Studio · **Qwen3-4B-Instruct-2507** (GGUF Q4_K_M) | externo |
| Datos | SQLite | `hiremind.db` |

Los diagramas de arquitectura, razonamiento y flujo de trabajo están en `../diagramas/`.

### Pantallas

- **`/`** · Landing de venta (hoy dentro de la app; está pensada para separarse a su propio sitio).
- **`/app`** · Panel: vacantes, CV evaluados, revisión manual, tiempo por CV, distribución de puntajes y actividad reciente.
- **`/app/vacantes`** · Lista de vacantes y ejemplos.
- **`/app/vacantes/:id`** · 1 · Criterios: tipo, peso, palabras clave; avisa si los pesos no suman 100 % y rechaza criterios discriminatorios.
- **`/app/vacantes/:id/cvs`** · 2 · Hojas de vida: arrastrar varios PDF, avance y tiempo por CV.
- **`/app/vacantes/:id/ranking`** · 3 · Ranking: top 5, justificación, citas verificadas por criterio, corrección humana que recalcula, datos extraídos, PDF original, revisión manual y exportación CSV.

Tema claro y oscuro; se adapta a celular.

## Cómo funciona cada CV

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

El orden de los pasos está en `agente/pipeline.py`. Python, no el modelo, decide el nivel de formación (a partir del título), si una carrera está en curso, las fechas de experiencia (a partir de la cita) y si una habilidad viene solo de un proyecto o curso.

## Requisitos

- PC con 16 GB de RAM (con GPU es más rápido, pero no es obligatoria)
- [LM Studio](https://lmstudio.ai) con **Qwen3-4B-Instruct-2507** (Q4_K_M)
- Python 3.12 y Node.js 20 o superior

## Instalación y uso

```bash
# 1. Modelo y servidor local
lms get qwen/qwen3-4b-2507@q4_k_m
lms load qwen/qwen3-4b-2507 --context-length 8192 --gpu max -y
lms server start                      # http://localhost:1234/v1

# 2. Backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Todo junto: compila la interfaz y abre http://localhost:8000
./iniciar.sh
```

En el panel hay un botón para cargar las 2 vacantes de ejemplo.

### Modo desarrollo (recarga en caliente)

```bash
.venv/bin/uvicorn api.main:app --reload --port 8000   # terminal 1
cd web && npm install && npm run dev                  # terminal 2 → http://localhost:5173
```

Vite reenvía `/api` al puerto 8000.

## API

| Método | Ruta | Uso |
|---|---|---|
| GET | `/api/estado` | ¿LM Studio responde y el modelo está cargado? |
| GET | `/api/resumen` | Números del panel |
| GET/POST | `/api/vacantes` | Listar / crear (422 con `errores` legibles si no es válida) |
| GET/PUT/DELETE | `/api/vacantes/{id}` | Ver / editar / borrar |
| POST | `/api/vacantes/demo` | Cargar las vacantes de ejemplo (sin duplicar) |
| POST | `/api/vacantes/{id}/cvs` | Evaluar un PDF (campo `archivo`) |
| GET | `/api/vacantes/{id}/ranking` | Ranking + revisión manual |
| GET | `/api/vacantes/{id}/ranking.csv` | Exportar |
| PATCH | `/api/evaluaciones/{eval_id}/criterios/{criterio_id}` | Corrección humana (`{"estado": "cumple"}`) |
| GET | `/api/candidatos/{id}/pdf` | PDF original |

Documentación interactiva en `http://localhost:8000/docs`.

## Datos de prueba

`datos/cvs/` tiene 15 hojas de vida **ficticias** (`scripts/generar_cvs.py`):

- CV 01 a 08 → vacante "Asistente contable"; CV 09 a 15 → "Desarrollador/a junior Python"
- `cv_08_escaneado.pdf`: solo imagen → debe ir a revisión manual
- `cv_13_trampa_disenador.pdf`: diseñador sin programación → el agente no debe inventarle Python
- Varios CV traen edad, estado civil o nacionalidad → deben excluirse antes del análisis

Resultado medido (Qwen3-4B Q4_K_M, GPU de 8 GB): 9,4 s por CV en promedio, P95 11,4 s; el escaneado va a revisión manual y el CV trampa obtiene 10/100.

## Pruebas

```bash
.venv/bin/python -m pytest              # reglas, equidad, evidencias, SQLite y API (sin LM Studio)
.venv/bin/python scripts/probar_lote.py # punta a punta con LM Studio: ranking y tiempos por CV
cd web && npm run typecheck             # tipos de la interfaz
```

## Configuración

Variables de entorno (ver `agente/config.py`): `HIREMIND_LLM_URL`, `HIREMIND_MODELO`, `HIREMIND_DB`, `HIREMIND_ARCHIVOS`.
Para usar otro modelo (por ejemplo uno de 8B) basta con cargarlo en LM Studio y cambiar `HIREMIND_MODELO`.
