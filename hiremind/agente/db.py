"""Persistencia local en SQLite: vacantes, candidatos, evaluaciones y evidencias."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from . import config
from .modelos import ResultadoCriterio, Vacante

ESQUEMA = """
CREATE TABLE IF NOT EXISTS vacantes (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    criterios_json TEXT NOT NULL,
    creada TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS candidatos (
    id INTEGER PRIMARY KEY,
    vacante_id INTEGER NOT NULL REFERENCES vacantes(id) ON DELETE CASCADE,
    archivo TEXT NOT NULL,
    nombre TEXT NOT NULL DEFAULT '',
    estado TEXT NOT NULL CHECK (estado IN ('evaluado', 'revision_manual')),
    motivo TEXT NOT NULL DEFAULT '',
    datos_quitados TEXT NOT NULL DEFAULT '[]',
    creado TEXT NOT NULL,
    UNIQUE (vacante_id, archivo)
);
CREATE TABLE IF NOT EXISTS evaluaciones (
    id INTEGER PRIMARY KEY,
    candidato_id INTEGER NOT NULL UNIQUE REFERENCES candidatos(id) ON DELETE CASCADE,
    puntaje REAL NOT NULL,
    justificacion TEXT NOT NULL,
    extraccion_json TEXT NOT NULL,
    segundos REAL NOT NULL,
    intentos INTEGER NOT NULL,
    corregida INTEGER NOT NULL DEFAULT 0,
    creada TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidencias (
    id INTEGER PRIMARY KEY,
    evaluacion_id INTEGER NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
    criterio_id TEXT NOT NULL,
    nombre TEXT NOT NULL,
    peso REAL NOT NULL,
    estado TEXT NOT NULL,
    detalle TEXT NOT NULL,
    citas_json TEXT NOT NULL,
    corregido INTEGER NOT NULL DEFAULT 0
);
"""


def _ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


@contextmanager
def conectar(path: str | None = None):
    con = sqlite3.connect(path or config.DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(ESQUEMA)
    try:
        yield con
        con.commit()
    finally:
        con.close()


# ---------------------------------------------------------------- vacantes
def guardar_vacante(con, vac: Vacante) -> int:
    criterios = json.dumps([c.model_dump() for c in vac.criterios], ensure_ascii=False)
    if vac.id:
        con.execute("UPDATE vacantes SET titulo=?, descripcion=?, criterios_json=? WHERE id=?",
                    (vac.titulo, vac.descripcion, criterios, vac.id))
        return vac.id
    cur = con.execute("INSERT INTO vacantes (titulo, descripcion, criterios_json, creada) VALUES (?,?,?,?)",
                      (vac.titulo, vac.descripcion, criterios, _ahora()))
    return cur.lastrowid


def listar_vacantes(con) -> list[Vacante]:
    filas = con.execute("SELECT * FROM vacantes ORDER BY id").fetchall()
    return [Vacante(id=f["id"], titulo=f["titulo"], descripcion=f["descripcion"],
                    criterios=json.loads(f["criterios_json"])) for f in filas]


def obtener_vacante(con, vacante_id: int) -> Vacante | None:
    return next((v for v in listar_vacantes(con) if v.id == vacante_id), None)


def borrar_vacante(con, vacante_id: int) -> bool:
    return con.execute("DELETE FROM vacantes WHERE id=?", (vacante_id,)).rowcount > 0


def estadisticas_vacantes(con) -> dict[int, dict]:
    """Por vacante: CV evaluados, en revisión manual, mejor puntaje y promedio."""
    out = {}
    for f in con.execute(
        "SELECT v.id, v.creada, "
        "SUM(c.estado='evaluado') AS evaluados, SUM(c.estado='revision_manual') AS revision, "
        "MAX(e.puntaje) AS mejor, AVG(e.puntaje) AS promedio, MAX(c.creado) AS ultima "
        "FROM vacantes v LEFT JOIN candidatos c ON c.vacante_id=v.id "
        "LEFT JOIN evaluaciones e ON e.candidato_id=c.id GROUP BY v.id"):
        out[f["id"]] = {"creada": f["creada"], "evaluados": f["evaluados"] or 0, "revision": f["revision"] or 0,
                        "mejor": f["mejor"], "promedio": round(f["promedio"], 1) if f["promedio"] is not None else None,
                        "ultima_actividad": f["ultima"]}
    return out


def resumen(con) -> dict:
    """Números del panel de inicio."""
    tot = con.execute(
        "SELECT (SELECT COUNT(*) FROM vacantes) AS vacantes, "
        "(SELECT COUNT(*) FROM candidatos WHERE estado='evaluado') AS evaluados, "
        "(SELECT COUNT(*) FROM candidatos WHERE estado='revision_manual') AS revision, "
        "(SELECT AVG(segundos) FROM evaluaciones) AS seg, "
        "(SELECT COUNT(*) FROM evaluaciones WHERE corregida=1) AS corregidas").fetchone()
    puntajes = [f[0] for f in con.execute("SELECT puntaje FROM evaluaciones")]
    rangos = [(0, 25), (25, 50), (50, 75), (75, 101)]
    distribucion = [{"rango": f"{a}–{min(b, 100)}", "cantidad": sum(a <= p < b for p in puntajes)} for a, b in rangos]
    recientes = [dict(f) for f in con.execute(
        "SELECT c.id, c.nombre, c.archivo, c.estado, c.creado, v.id AS vacante_id, v.titulo AS vacante, "
        "e.puntaje FROM candidatos c JOIN vacantes v ON v.id=c.vacante_id "
        "LEFT JOIN evaluaciones e ON e.candidato_id=c.id ORDER BY c.creado DESC, c.id DESC LIMIT 8")]
    return {"vacantes": tot["vacantes"], "evaluados": tot["evaluados"], "revision": tot["revision"],
            "segundos_promedio": round(tot["seg"], 1) if tot["seg"] is not None else None,
            "corregidas": tot["corregidas"], "distribucion": distribucion, "recientes": recientes}


# ---------------------------------------------------------------- candidatos y evaluaciones
def borrar_candidato(con, vacante_id: int, archivo: str) -> None:
    con.execute("DELETE FROM candidatos WHERE vacante_id=? AND archivo=?", (vacante_id, archivo))


def guardar_revision_manual(con, vacante_id: int, archivo: str, motivo: str) -> int:
    borrar_candidato(con, vacante_id, archivo)
    cur = con.execute(
        "INSERT INTO candidatos (vacante_id, archivo, estado, motivo, creado) VALUES (?,?,?,?,?)",
        (vacante_id, archivo, "revision_manual", motivo, _ahora()))
    return cur.lastrowid


def guardar_evaluacion(con, vacante_id: int, archivo: str, nombre: str, datos_quitados: list[str],
                       puntaje: float, justificacion: str, extraccion: dict, segundos: float,
                       intentos: int, resultados: list[ResultadoCriterio]) -> int:
    borrar_candidato(con, vacante_id, archivo)
    cid = con.execute(
        "INSERT INTO candidatos (vacante_id, archivo, nombre, estado, datos_quitados, creado) "
        "VALUES (?,?,?,?,?,?)",
        (vacante_id, archivo, nombre, "evaluado", json.dumps(datos_quitados, ensure_ascii=False), _ahora()),
    ).lastrowid
    eid = con.execute(
        "INSERT INTO evaluaciones (candidato_id, puntaje, justificacion, extraccion_json, segundos, "
        "intentos, creada) VALUES (?,?,?,?,?,?,?)",
        (cid, puntaje, justificacion, json.dumps(extraccion, ensure_ascii=False), segundos, intentos, _ahora()),
    ).lastrowid
    con.executemany(
        "INSERT INTO evidencias (evaluacion_id, criterio_id, nombre, peso, estado, detalle, citas_json) "
        "VALUES (?,?,?,?,?,?,?)",
        [(eid, r.criterio_id, r.nombre, r.peso, r.estado, r.detalle,
          json.dumps(r.citas, ensure_ascii=False)) for r in resultados])
    return cid


def ranking(con, vacante_id: int) -> list[dict]:
    """Candidatos evaluados ordenados por puntaje (todos; no se descarta a nadie)."""
    filas = con.execute(
        "SELECT c.id, c.archivo, c.nombre, c.datos_quitados, e.id AS eval_id, e.puntaje, "
        "e.justificacion, e.segundos, e.intentos, e.corregida, e.extraccion_json "
        "FROM candidatos c JOIN evaluaciones e ON e.candidato_id = c.id "
        "WHERE c.vacante_id = ? ORDER BY e.puntaje DESC, c.nombre", (vacante_id,)).fetchall()
    out = []
    for f in filas:
        d = dict(f)
        d["datos_quitados"] = json.loads(d["datos_quitados"])
        d["extraccion"] = json.loads(d.pop("extraccion_json"))
        d["criterios"] = [
            ResultadoCriterio(criterio_id=r["criterio_id"], nombre=r["nombre"], peso=r["peso"],
                              estado=r["estado"], detalle=r["detalle"],
                              citas=json.loads(r["citas_json"]), corregido=bool(r["corregido"]))
            for r in con.execute("SELECT * FROM evidencias WHERE evaluacion_id=? ORDER BY id", (f["eval_id"],))
        ]
        out.append(d)
    return out


def revision_manual(con, vacante_id: int) -> list[dict]:
    return [dict(f) for f in con.execute(
        "SELECT id, archivo, motivo, creado FROM candidatos WHERE vacante_id=? AND estado='revision_manual' "
        "ORDER BY archivo", (vacante_id,))]


def candidato(con, candidato_id: int) -> dict | None:
    f = con.execute("SELECT id, vacante_id, archivo FROM candidatos WHERE id=?", (candidato_id,)).fetchone()
    return dict(f) if f else None


def evaluacion_de(con, eval_id: int) -> dict | None:
    f = con.execute("SELECT e.id, c.vacante_id FROM evaluaciones e JOIN candidatos c ON c.id=e.candidato_id "
                    "WHERE e.id=?", (eval_id,)).fetchone()
    return dict(f) if f else None


def corregir_criterio(con, eval_id: int, criterio_id: str, nuevo_estado: str) -> float:
    """La persona corrige un criterio: se guarda y se recalcula el puntaje con Python."""
    con.execute("UPDATE evidencias SET estado=?, corregido=1 WHERE evaluacion_id=? AND criterio_id=?",
                (nuevo_estado, eval_id, criterio_id))
    filas = con.execute("SELECT peso, estado FROM evidencias WHERE evaluacion_id=?", (eval_id,)).fetchall()
    from .modelos import VALOR_ESTADO
    nuevo = round(sum(f["peso"] * VALOR_ESTADO[f["estado"]] for f in filas), 1)
    con.execute("UPDATE evaluaciones SET puntaje=?, corregida=1 WHERE id=?", (nuevo, eval_id))
    return nuevo
