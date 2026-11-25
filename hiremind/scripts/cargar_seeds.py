"""Carga las vacantes de prueba de datos/seeds/ y evalúa sus CV (necesita LM Studio encendido).

    .venv/bin/python scripts/cargar_seeds.py                   # las 4 vacantes con todos sus CV
    .venv/bin/python scripts/cargar_seeds.py cocinero -n 5     # una vacante, solo 5 CV
    .venv/bin/python scripts/cargar_seeds.py --sin-evaluar     # solo crear las vacantes (suba los PDF desde la app)

Si la vacante ya existe (mismo título) se reutiliza y los CV ya cargados se saltan (--reevaluar para repetirlos).
"""
import argparse
import shutil
import sys
import time
from itertools import zip_longest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agente import config, db, llm  # noqa: E402
from agente.pipeline import evaluar_cv  # noqa: E402
from agente.seeds import VACANTES_SEEDS, archivos  # noqa: E402

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("carpetas", nargs="*", help=f"vacantes a cargar: {', '.join(VACANTES_SEEDS)} (por defecto, todas)")
p.add_argument("-n", type=int, default=0, help="máximo de CV por vacante")
p.add_argument("--sin-evaluar", action="store_true")
p.add_argument("--reevaluar", action="store_true", help="volver a evaluar CV ya cargados")
a = p.parse_args()
if desconocidas := set(a.carpetas) - set(VACANTES_SEEDS):
    p.error(f"no existe: {', '.join(desconocidas)}")

if not a.sin_evaluar:
    ok, msg = llm.servidor_disponible()
    if not ok:
        sys.exit(f"{msg}\nEncienda LM Studio o use --sin-evaluar.")

with db.conectar() as con:
    # 1. Crear primero TODAS las vacantes, así aparecen de inmediato en la app
    existentes = {v.titulo: v for v in db.listar_vacantes(con)}
    vacantes = {}
    for carpeta in a.carpetas or VACANTES_SEEDS:
        vac = VACANTES_SEEDS[carpeta].model_copy()
        vac.id = existentes[vac.titulo].id if vac.titulo in existentes else db.guardar_vacante(con, vac)
        vacantes[carpeta] = vac
        print(f"▸ {vac.titulo} (vacante {vac.id}, {len(archivos(carpeta))} CV)")
    con.commit()
    if a.sin_evaluar:
        sys.exit()

    # 2. Evaluar intercalando vacantes (un CV de cada una por turno) para que todos los rankings se llenen a la vez.
    #    Los CV ya cargados se saltan, salvo con --reevaluar.
    colas = []
    for carpeta, vac in vacantes.items():
        hechos = {f["archivo"] for f in con.execute("SELECT archivo FROM candidatos WHERE vacante_id=?", (vac.id,))}
        colas.append([(vac, p) for p in archivos(carpeta)[: a.n or None] if a.reevaluar or p.name not in hechos])
    pendientes = [x for grupo in zip_longest(*colas) for x in grupo if x]
    print(f"\n{len(pendientes)} CV por evaluar\n")
    for i, (vac, pdf) in enumerate(pendientes, 1):
        destino = Path(config.ARCHIVOS_DIR) / str(vac.id) / pdf.name
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pdf, destino)
        t = time.perf_counter()
        r = evaluar_cv(con, vac, pdf.name, pdf.read_bytes())
        con.commit()
        res = f"{r.puntaje:5.1f}" if r.estado == "evaluado" else "  —  revisión manual: " + r.motivo
        print(f"  {i:2}/{len(pendientes)} {vac.titulo.split(' · ')[0][:22]:22} {pdf.name:42} {res}  ({time.perf_counter() - t:.1f} s)")
