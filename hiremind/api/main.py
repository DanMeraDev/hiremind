"""API local de HireMind (FastAPI). La interfaz en React solo habla con esta API.

    uvicorn api.main:app --port 8000

Si existe web/dist (la interfaz compilada), también se sirve desde aquí en /.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

from agente import config, db, llm
from agente.demo import VACANTES_DEMO
from agente.modelos import Estado, Vacante
from agente.pipeline import evaluar_cv

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web" / "dist"

app = FastAPI(title="HireMind API", version="1.0")


# ---------------------------------------------------------------- utilidades
def _errores(e: ValidationError) -> list[str]:
    return [str(x["msg"]).removeprefix("Value error, ") for x in e.errors()]


def _vacante_o_404(con, vacante_id: int) -> Vacante:
    vac = db.obtener_vacante(con, vacante_id)
    if vac is None:
        raise HTTPException(404, "La vacante no existe")
    return vac


def _ruta_pdf(vacante_id: int, archivo: str) -> Path:
    return Path(config.ARCHIVOS_DIR) / str(vacante_id) / Path(archivo).name


def _vacante_json(vac: Vacante, stats: dict) -> dict:
    return {**vac.model_dump(), **stats.get(vac.id, {})}


# ---------------------------------------------------------------- estado y panel
@app.get("/api/estado")
def estado():
    ok, mensaje = llm.servidor_disponible()
    return {"llm_ok": ok, "mensaje": mensaje, "modelo": config.MODELO, "url": config.LLM_URL,
            "top_n": config.TOP_N}


@app.get("/api/resumen")
def resumen():
    with db.conectar() as con:
        datos = db.resumen(con)
        stats = db.estadisticas_vacantes(con)
        datos["por_vacante"] = [_vacante_json(v, stats) for v in db.listar_vacantes(con)]
    return datos


# ---------------------------------------------------------------- vacantes
@app.get("/api/vacantes")
def listar_vacantes():
    with db.conectar() as con:
        stats = db.estadisticas_vacantes(con)
        return [_vacante_json(v, stats) for v in db.listar_vacantes(con)]


@app.get("/api/vacantes/{vacante_id}")
def obtener_vacante(vacante_id: int):
    with db.conectar() as con:
        return _vacante_json(_vacante_o_404(con, vacante_id), db.estadisticas_vacantes(con))


def _guardar(datos: dict, vacante_id: int | None = None):
    try:
        vac = Vacante.model_validate({**datos, "id": vacante_id})
    except ValidationError as e:
        return JSONResponse({"errores": _errores(e)}, status_code=422)
    with db.conectar() as con:
        if vacante_id is not None:
            _vacante_o_404(con, vacante_id)
        vid = db.guardar_vacante(con, vac)
        return _vacante_json(db.obtener_vacante(con, vid), db.estadisticas_vacantes(con))


@app.post("/api/vacantes", status_code=201)
def crear_vacante(datos: dict):
    return _guardar(datos)


@app.put("/api/vacantes/{vacante_id}")
def actualizar_vacante(vacante_id: int, datos: dict):
    return _guardar(datos, vacante_id)


@app.delete("/api/vacantes/{vacante_id}", status_code=204)
def borrar_vacante(vacante_id: int):
    with db.conectar() as con:
        if not db.borrar_vacante(con, vacante_id):
            raise HTTPException(404, "La vacante no existe")


@app.post("/api/vacantes/demo")
def cargar_demo():
    """Carga las 2 vacantes de ejemplo (si ya existen, no las duplica)."""
    with db.conectar() as con:
        existentes = {v.titulo for v in db.listar_vacantes(con)}
        nuevas = [db.guardar_vacante(con, v) for v in VACANTES_DEMO if v.titulo not in existentes]
    return {"creadas": len(nuevas)}


# ---------------------------------------------------------------- hojas de vida
@app.post("/api/vacantes/{vacante_id}/cvs")
def subir_cv(vacante_id: int, archivo: UploadFile = File(...)):
    """Evalúa una hoja de vida (pasos 1-8). La interfaz envía los PDF de uno en uno para mostrar el avance."""
    nombre = Path(archivo.filename or "cv.pdf").name
    datos = archivo.file.read()
    with db.conectar() as con:
        vac = _vacante_o_404(con, vacante_id)
        ruta = _ruta_pdf(vacante_id, nombre)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_bytes(datos)
        r = evaluar_cv(con, vac, nombre, datos)
    return {"archivo": r.archivo, "estado": r.estado, "motivo": r.motivo, "nombre": r.nombre,
            "puntaje": r.puntaje, "segundos": round(r.segundos, 1), "intentos": r.intentos,
            "no_verificados": r.no_verificados, "datos_quitados": r.datos_quitados}


@app.get("/api/vacantes/{vacante_id}/ranking")
def ranking(vacante_id: int):
    with db.conectar() as con:
        _vacante_o_404(con, vacante_id)
        filas = db.ranking(con, vacante_id)
        manual = db.revision_manual(con, vacante_id)
    for i, f in enumerate(filas, 1):
        f["posicion"] = i
        f["top"] = i <= config.TOP_N
        f["criterios"] = [c.model_dump() for c in f["criterios"]]
    return {"candidatos": filas, "revision_manual": manual, "top_n": config.TOP_N}


@app.get("/api/vacantes/{vacante_id}/ranking.csv")
def ranking_csv(vacante_id: int):
    with db.conectar() as con:
        vac = _vacante_o_404(con, vacante_id)
        filas = db.ranking(con, vacante_id)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["posicion", "candidato", "archivo", "puntaje", "corregido",
                *[c.nombre for c in vac.criterios], "justificacion"])
    for i, f in enumerate(filas, 1):
        estados = {c.criterio_id: c.estado.replace("_", " ") for c in f["criterios"]}
        w.writerow([i, f["nombre"], f["archivo"], f["puntaje"], "sí" if f["corregida"] else "no",
                    *[estados.get(c.id, "") for c in vac.criterios], f["justificacion"]])
    return Response("﻿" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="ranking_vacante_{vacante_id}.csv"'})


@app.get("/api/candidatos/{candidato_id}/pdf")
def pdf_original(candidato_id: int):
    with db.conectar() as con:
        c = db.candidato(con, candidato_id)
    if c is None:
        raise HTTPException(404, "El candidato no existe")
    ruta = _ruta_pdf(c["vacante_id"], c["archivo"])
    if not ruta.exists():
        raise HTTPException(404, "No hay copia del PDF original")
    return FileResponse(ruta, media_type="application/pdf",
                        headers={"Content-Disposition": f'inline; filename="{ruta.name}"'})


# ---------------------------------------------------------------- corrección humana
class Correccion(BaseModel):
    estado: Estado


@app.patch("/api/evaluaciones/{eval_id}/criterios/{criterio_id}")
def corregir(eval_id: int, criterio_id: str, body: Correccion):
    with db.conectar() as con:
        if db.evaluacion_de(con, eval_id) is None:
            raise HTTPException(404, "La evaluación no existe")
        return {"puntaje": db.corregir_criterio(con, eval_id, criterio_id, body.estado)}


# ---------------------------------------------------------------- interfaz compilada
if WEB.exists():
    app.mount("/assets", StaticFiles(directory=WEB / "assets"), name="assets")

    @app.get("/{ruta:path}", include_in_schema=False)
    def spa(ruta: str):
        archivo = WEB / ruta
        if ruta and archivo.is_file() and WEB in archivo.resolve().parents:
            return FileResponse(archivo)
        return FileResponse(WEB / "index.html")
