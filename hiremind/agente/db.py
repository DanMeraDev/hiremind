"""Persistencia local en SQLite: vacantes, candidatos, evaluaciones y evidencias."""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from . import config
from .modelos import ResultadoCriterio, Vacante

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY,
    usuario TEXT NOT NULL UNIQUE COLLATE NOCASE,
    nombre TEXT NOT NULL,
    clave_hash TEXT NOT NULL,
    creado TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sesiones (
    token TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    creada TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS vacantes (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
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
CREATE TABLE IF NOT EXISTS selecciones (
    id INTEGER PRIMARY KEY,
    candidato_id INTEGER NOT NULL UNIQUE REFERENCES candidatos(id) ON DELETE CASCADE,
    correo TEXT NOT NULL,
    correo_enviado TEXT,
    preguntas_json TEXT NOT NULL DEFAULT '[]',
    origen_preguntas TEXT NOT NULL DEFAULT '',
    creada TEXT NOT NULL
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
    _migrar(con)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def _migrar(con) -> None:
    """Bases creadas antes del inicio de sesión: la vacante aún no tenía dueño."""
    if "usuario_id" not in {f["name"] for f in con.execute("PRAGMA table_info(vacantes)")}:
        con.execute("ALTER TABLE vacantes ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE")


# ---------------------------------------------------------------- usuarios y sesiones
def _hash(clave: str, sal: bytes | None = None) -> str:
    sal = sal or secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", clave.encode(), sal, 200_000)
    return f"{sal.hex()}${h.hex()}"


def crear_usuario(con, usuario: str, nombre: str, clave: str) -> int:
    """Crea la cuenta o, si ya existe, actualiza su nombre y contraseña."""
    f = con.execute("SELECT id FROM usuarios WHERE usuario=?", (usuario,)).fetchone()
    if f:
        con.execute("UPDATE usuarios SET nombre=?, clave_hash=? WHERE id=?", (nombre, _hash(clave), f["id"]))
        return f["id"]
    return con.execute("INSERT INTO usuarios (usuario, nombre, clave_hash, creado) VALUES (?,?,?,?)",
                       (usuario, nombre, _hash(clave), _ahora())).lastrowid


def verificar_clave(con, usuario: str, clave: str) -> dict | None:
    f = con.execute("SELECT id, usuario, nombre, clave_hash FROM usuarios WHERE usuario=?", (usuario.strip(),)).fetchone()
    if f is None:
        _hash(clave)  # mismo tiempo de respuesta exista o no el usuario
        return None
    sal, _ = f["clave_hash"].split("$")
    if not hmac.compare_digest(_hash(clave, bytes.fromhex(sal)), f["clave_hash"]):
        return None
    return {"id": f["id"], "usuario": f["usuario"], "nombre": f["nombre"]}


def abrir_sesion(con, usuario_id: int) -> str:
    token = secrets.token_urlsafe(32)
    con.execute("INSERT INTO sesiones (token, usuario_id, creada) VALUES (?,?,?)", (token, usuario_id, _ahora()))
    return token


def usuario_de_sesion(con, token: str) -> dict | None:
    f = con.execute("SELECT u.id, u.usuario, u.nombre FROM sesiones s JOIN usuarios u ON u.id=s.usuario_id "
                    "WHERE s.token=?", (token,)).fetchone()
    return dict(f) if f else None


def cerrar_sesion(con, token: str) -> None:
    con.execute("DELETE FROM sesiones WHERE token=?", (token,))


def asignar_huerfanas(con, usuario_id: int, titulo: str | None = None) -> int:
    """Vacantes sin dueño (creadas antes del inicio de sesión) pasan a este usuario; con titulo, solo esas."""
    if titulo is None:
        return con.execute("UPDATE vacantes SET usuario_id=? WHERE usuario_id IS NULL", (usuario_id,)).rowcount
    return con.execute("UPDATE vacantes SET usuario_id=? WHERE usuario_id IS NULL AND titulo=?",
                       (usuario_id, titulo)).rowcount


# ---------------------------------------------------------------- vacantes
def guardar_vacante(con, vac: Vacante, usuario_id: int | None = None) -> int:
    criterios = json.dumps([c.model_dump() for c in vac.criterios], ensure_ascii=False)
    if vac.id:
        con.execute("UPDATE vacantes SET titulo=?, descripcion=?, criterios_json=? WHERE id=?",
                    (vac.titulo, vac.descripcion, criterios, vac.id))
        return vac.id
    cur = con.execute("INSERT INTO vacantes (usuario_id, titulo, descripcion, criterios_json, creada) "
                      "VALUES (?,?,?,?,?)", (usuario_id, vac.titulo, vac.descripcion, criterios, _ahora()))
    return cur.lastrowid


def listar_vacantes(con, usuario_id: int | None = None) -> list[Vacante]:
    """Con usuario_id, solo las de ese usuario; sin él, todas (scripts y pruebas)."""
    if usuario_id is None:
        filas = con.execute("SELECT * FROM vacantes ORDER BY id").fetchall()
    else:
        filas = con.execute("SELECT * FROM vacantes WHERE usuario_id=? ORDER BY id", (usuario_id,)).fetchall()
    return [Vacante(id=f["id"], titulo=f["titulo"], descripcion=f["descripcion"],
                    criterios=json.loads(f["criterios_json"])) for f in filas]


def obtener_vacante(con, vacante_id: int, usuario_id: int | None = None) -> Vacante | None:
    return next((v for v in listar_vacantes(con, usuario_id) if v.id == vacante_id), None)


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


def resumen(con, usuario_id: int | None = None) -> dict:
    """Números del panel de inicio (de un usuario, o de todos sin usuario_id)."""
    filtro = "" if usuario_id is None else "WHERE usuario_id = :u"
    mias = f"(SELECT id FROM vacantes {filtro})"
    cands = f"FROM candidatos WHERE vacante_id IN {mias}"
    evals = f"FROM evaluaciones WHERE candidato_id IN (SELECT id {cands})"
    p = {"u": usuario_id}
    tot = con.execute(
        f"SELECT (SELECT COUNT(*) FROM vacantes {filtro}) AS vacantes, "
        f"(SELECT COUNT(*) {cands} AND estado='evaluado') AS evaluados, "
        f"(SELECT COUNT(*) {cands} AND estado='revision_manual') AS revision, "
        f"(SELECT AVG(segundos) {evals}) AS seg, "
        f"(SELECT COUNT(*) {evals} AND corregida=1) AS corregidas", p).fetchone()
    puntajes = [f[0] for f in con.execute(f"SELECT puntaje {evals}", p)]
    rangos = [(0, 25), (25, 50), (50, 75), (75, 101)]
    distribucion = [{"rango": f"{a}–{min(b, 100)}", "cantidad": sum(a <= p < b for p in puntajes)} for a, b in rangos]
    recientes = [dict(f) for f in con.execute(
        "SELECT c.id, c.nombre, c.archivo, c.estado, c.creado, v.id AS vacante_id, v.titulo AS vacante, "
        "e.puntaje FROM candidatos c JOIN vacantes v ON v.id=c.vacante_id "
        f"LEFT JOIN evaluaciones e ON e.candidato_id=c.id WHERE v.id IN {mias} "
        "ORDER BY c.creado DESC, c.id DESC LIMIT 8", p)]
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
        "e.justificacion, e.segundos, e.intentos, e.corregida, e.extraccion_json, "
        "s.correo AS sel_correo, s.correo_enviado AS sel_enviado, s.preguntas_json AS sel_preguntas, "
        "s.origen_preguntas AS sel_origen, s.creada AS sel_creada "
        "FROM candidatos c JOIN evaluaciones e ON e.candidato_id = c.id "
        "LEFT JOIN selecciones s ON s.candidato_id = c.id "
        "WHERE c.vacante_id = ? ORDER BY e.puntaje DESC, c.nombre", (vacante_id,)).fetchall()
    out = []
    for f in filas:
        d = dict(f)
        d["datos_quitados"] = json.loads(d["datos_quitados"])
        d["extraccion"] = json.loads(d.pop("extraccion_json"))
        sel = {k[4:]: d.pop(k) for k in list(d) if k.startswith("sel_")}
        d["seleccion"] = None if sel["creada"] is None else {
            "correo": sel["correo"], "correo_enviado": sel["enviado"], "creada": sel["creada"],
            "preguntas": json.loads(sel["preguntas"]), "origen_preguntas": sel["origen"]}
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


# ---------------------------------------------------------------- selección del candidato
def guardar_seleccion(con, candidato_id: int, correo: str, enviado: str | None,
                      preguntas: list[dict], origen: str) -> None:
    con.execute(
        "INSERT INTO selecciones (candidato_id, correo, correo_enviado, preguntas_json, origen_preguntas, creada) "
        "VALUES (?,?,?,?,?,?) ON CONFLICT(candidato_id) DO UPDATE SET correo=excluded.correo, "
        "correo_enviado=COALESCE(excluded.correo_enviado, selecciones.correo_enviado), "
        "preguntas_json=excluded.preguntas_json, origen_preguntas=excluded.origen_preguntas",
        (candidato_id, correo, enviado, json.dumps(preguntas, ensure_ascii=False), origen, _ahora()))


def quitar_seleccion(con, candidato_id: int) -> bool:
    return con.execute("DELETE FROM selecciones WHERE candidato_id=?", (candidato_id,)).rowcount > 0
