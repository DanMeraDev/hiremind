"""Costo computacional: tiempo por etapa, tokens/s y recursos con 1 y N usuarios a la vez.

    .venv/bin/python scripts/benchmark.py                 # 5 CV por vacante (20), 1 y 3 usuarios
    .venv/bin/python scripts/benchmark.py -n 3 -u 1 3 5   # otra carga

Usa los CV de datos/seeds/ (siempre los mismos, en orden) y una base temporal; no envía correos.
Requiere LM Studio con el modelo cargado (para N usuarios: lms load ... --parallel N).
Guarda el resultado en evaluacion/benchmark.json.
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import psutil
from openai.resources.chat.completions import Completions

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from agente import db, entrevista, equidad, evidencia, llm, pipeline, puntuacion  # noqa: E402
from agente.seeds import VACANTES_SEEDS, archivos  # noqa: E402

_local = threading.local()


def _registro() -> dict:
    return _local.__dict__.setdefault("r", {"etapas": {}, "llamadas": []})


def _medir(modulo, nombre: str, etapa: str) -> None:
    original = getattr(modulo, nombre)

    def envoltura(*a, **k):
        t0 = time.perf_counter()
        try:
            return original(*a, **k)
        finally:
            et = _registro()["etapas"]
            et[etapa] = et.get(etapa, 0.0) + time.perf_counter() - t0
    setattr(modulo, nombre, envoltura)


# Etapas del pipeline (se envuelven las funciones reales, sin cambiar la app)
_medir(pipeline, "leer_pdf", "leer_pdf")
_medir(equidad, "limpiar_texto", "quitar_datos")
_medir(llm, "extraer", "llm_extraccion")
_medir(evidencia, "verificar", "verificar_citas")
_medir(puntuacion, "evaluar_criterios", "puntuar")
_medir(llm, "justificar", "llm_justificacion")
_medir(db, "guardar_evaluacion", "guardar_db")

# Cada llamada al modelo: tokens y duración
_crear = Completions.create


def _crear_medido(self, *a, **k):
    t0 = time.perf_counter()
    resp = _crear(self, *a, **k)
    u = resp.usage
    _registro()["llamadas"].append({"s": time.perf_counter() - t0,
                                    "entrada": getattr(u, "prompt_tokens", 0) or 0,
                                    "salida": getattr(u, "completion_tokens", 0) or 0})
    return resp


Completions.create = _crear_medido


class Muestreo(threading.Thread):
    """CPU, RAM, swap y memoria de LM Studio cada 0,5 s."""

    def __init__(self):
        super().__init__(daemon=True)
        self.parar = threading.Event()
        self.datos: list[dict] = []

    @staticmethod
    def _rss_modelo() -> int:
        total = 0
        for p in psutil.process_iter(["name", "cmdline", "memory_info"]):
            try:
                txt = (p.info["name"] or "") + " " + " ".join(p.info["cmdline"] or [])
                if "lmstudio" in txt.lower() or "lm studio" in txt.lower() or "llmworker" in txt.lower():
                    total += p.info["memory_info"].rss
            except (psutil.Error, TypeError):
                pass
        return total

    def run(self):
        psutil.cpu_percent()
        while not self.parar.wait(0.5):
            vm, sw = psutil.virtual_memory(), psutil.swap_memory()
            self.datos.append({"cpu": psutil.cpu_percent(), "ram_gb": (vm.total - vm.available) / 1e9,
                               "swap_gb": sw.used / 1e9, "lmstudio_gb": self._rss_modelo() / 1e9})


def _p(valores: list[float], q: float) -> float:
    v = sorted(valores)
    return v[min(len(v) - 1, round(q * (len(v) - 1)))] if v else 0.0


def correr(cvs: list[tuple[str, Path]], usuarios: int, ruta_db: str) -> dict:
    vac_ids: dict[str, int] = {}
    with db.conectar(ruta_db) as con:
        for carpeta in {c for c, _ in cvs}:
            vac_ids[carpeta] = db.guardar_vacante(con, VACANTES_SEEDS[carpeta])

    def un_cv(item):
        carpeta, pdf = item
        _local.__dict__.pop("r", None)
        vac = VACANTES_SEEDS[carpeta].model_copy(update={"id": vac_ids[carpeta]})
        with db.conectar(ruta_db) as con:  # cada usuario con su propia conexión, como en la app
            t0 = time.perf_counter()
            try:
                r = pipeline.evaluar_cv(con, vac, pdf.name, pdf.read_bytes())
                con.commit()
                estado, error = r.estado, ""
            except Exception as e:  # noqa: BLE001
                estado, error = "error", f"{type(e).__name__}: {e}"[:200]
            total = time.perf_counter() - t0
        reg = _registro()
        return {"vacante": carpeta, "estado": estado, "error": error, "segundos": total,
                "etapas": reg["etapas"], "llamadas": reg["llamadas"]}

    m = Muestreo()
    m.start()
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=usuarios) as ex:
        filas = list(ex.map(un_cv, cvs))
    pared = time.perf_counter() - t0
    m.parar.set()
    m.join()

    ok = [f for f in filas if f["estado"] == "evaluado"]
    lat = [f["segundos"] for f in ok]
    etapas: dict[str, float] = {}
    for f in ok:
        for k, v in f["etapas"].items():
            etapas[k] = etapas.get(k, 0.0) + v
    llamadas = [c for f in ok for c in f["llamadas"]]
    sal = sum(c["salida"] for c in llamadas)
    ent = sum(c["entrada"] for c in llamadas)
    t_llm = sum(c["s"] for c in llamadas)
    md = m.datos or [{"cpu": 0, "ram_gb": 0, "swap_gb": 0, "lmstudio_gb": 0}]
    return {
        "usuarios": usuarios, "cv": len(filas), "evaluados": len(ok),
        "revision_manual": sum(f["estado"] == "revision_manual" for f in filas),
        "errores": [f["error"] for f in filas if f["estado"] == "error"],
        "segundos_totales": round(pared, 1),
        "cv_por_minuto": round(len(ok) / pared * 60, 2),
        "latencia_s": {"promedio": round(statistics.mean(lat), 1) if lat else 0,
                       "p50": round(_p(lat, .5), 1), "p95": round(_p(lat, .95), 1), "max": round(max(lat, default=0), 1)},
        "etapas_promedio_s": {k: round(v / len(ok), 3) for k, v in etapas.items()} if ok else {},
        "tokens_por_cv": {"entrada": round(ent / max(len(ok), 1)), "salida": round(sal / max(len(ok), 1))},
        "tokens_s_por_usuario": round(sal / t_llm, 1) if t_llm else 0,
        "tokens_s_total": round(sal / pared, 1),
        "llamadas_llm_por_cv": round(len(llamadas) / max(len(ok), 1), 2),
        "recursos": {"cpu_prom": round(statistics.mean(d["cpu"] for d in md)),
                     "cpu_max": round(max(d["cpu"] for d in md)),
                     "ram_pico_gb": round(max(d["ram_gb"] for d in md), 2),
                     "swap_pico_gb": round(max(d["swap_gb"] for d in md), 2),
                     "lmstudio_pico_gb": round(max(d["lmstudio_gb"] for d in md), 2)},
        "por_cv": filas,
    }


def preguntas(ruta_db: str, n: int = 3) -> dict:
    """Tiempo de generar las preguntas de entrevista (paso 8) para los n mejores, como lo hace la app."""
    tiempos = []
    with db.conectar(ruta_db) as con:
        for vac in db.listar_vacantes(con):
            for fila in db.ranking(con, vac.id)[:1]:
                if len(tiempos) >= n:
                    break
                t0 = time.perf_counter()
                _, origen = entrevista.sugerir(vac, fila["criterios"], fila["extraccion"])
                tiempos.append({"s": round(time.perf_counter() - t0, 1), "origen": origen})
    return {"n": len(tiempos), "detalle": tiempos,
            "promedio_s": round(statistics.mean(t["s"] for t in tiempos), 1) if tiempos else None}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", type=int, default=5, help="CV por vacante")
    ap.add_argument("-u", type=int, nargs="+", default=[1, 3], help="usuarios simultáneos a probar")
    a = ap.parse_args()
    ok, info = llm.servidor_disponible()
    if not ok:
        sys.exit(f"LM Studio no está listo: {info}")
    cvs = [(c, p) for c in VACANTES_SEEDS for p in archivos(c)[: a.n]]
    vm = psutil.virtual_memory()
    salida = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "modelo": info,
              "equipo": {"cpu": platform.processor() or platform.machine(), "nucleos": psutil.cpu_count(),
                         "ram_gb": round(vm.total / 1e9, 1)},
              "corridas": []}
    with tempfile.TemporaryDirectory() as tmp:
        for u in a.u:
            ruta = str(Path(tmp) / f"bench_{u}.db")
            print(f"== {u} usuario(s), {len(cvs)} CV ...", flush=True)
            r = correr(cvs, u, ruta)
            if u == a.u[0]:
                try:
                    salida["preguntas_entrevista"] = preguntas(ruta)
                except Exception as e:  # noqa: BLE001
                    salida["preguntas_entrevista"] = {"error": str(e)[:200]}
            salida["corridas"].append(r)
            print({k: v for k, v in r.items() if k != "por_cv"}, flush=True)
    destino = RAIZ / "evaluacion" / "benchmark.json"
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=1))
    print("guardado en", destino)


if __name__ == "__main__":
    main()
