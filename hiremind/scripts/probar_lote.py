"""Prueba de punta a punta con LM Studio: evalúa todos los CV de ejemplo y muestra el ranking.

Uso:  python scripts/probar_lote.py [ruta_db]
Requiere LM Studio con el modelo cargado y el servidor encendido.
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from agente import db, llm  # noqa: E402
from agente.demo import VACANTES_DEMO  # noqa: E402
from agente.pipeline import evaluar_cv  # noqa: E402

# Qué CV se postulan a cada vacante de ejemplo
POSTULACIONES = {0: [f"cv_0{i}" for i in range(1, 9)], 1: [f"cv_{i:02d}" for i in range(9, 16)]}


def main(ruta_db: str) -> None:
    ok, info = llm.servidor_disponible()
    if not ok:
        sys.exit(f"LM Studio no está listo: {info}")
    Path(ruta_db).unlink(missing_ok=True)  # cada corrida empieza limpia
    cvs = sorted((RAIZ / "datos" / "cvs").glob("*.pdf"))
    tiempos = []
    with db.conectar(ruta_db) as con:
        for idx, vac in enumerate(VACANTES_DEMO):
            vac = vac.model_copy(update={"id": db.guardar_vacante(con, vac)})
            print(f"\n=== {vac.titulo}")
            for pdf in [p for p in cvs if p.name[:5] in POSTULACIONES[idx]]:
                r = evaluar_cv(con, vac, pdf.name, pdf.read_bytes())
                con.commit()
                if r.estado == "evaluado":
                    tiempos.append(r.segundos)
                    estados = " ".join(f"{c.criterio_id}={c.estado[:2]}" for c in r.criterios)
                    print(f"  {pdf.name:30s} {r.puntaje:5.1f}  {r.segundos:5.1f}s  int={r.intentos} "
                          f"noverif={r.no_verificados} quitados={r.datos_quitados}  {estados}")
                else:
                    print(f"  {pdf.name:30s} REVISIÓN MANUAL: {r.motivo}")
            print("  --- ranking")
            for i, f in enumerate(db.ranking(con, vac.id), 1):
                print(f"  {'*' if i <= 5 else ' '}{i:2d}. {f['puntaje']:5.1f}  {f['nombre']}")
            print("  justificación #1:", db.ranking(con, vac.id)[0]["justificacion"])
    if tiempos:
        tiempos.sort()
        p95 = tiempos[min(len(tiempos) - 1, round(0.95 * (len(tiempos) - 1)))]
        print(f"\nTiempo por CV: promedio {statistics.mean(tiempos):.1f}s · P95 {p95:.1f}s · n={len(tiempos)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "prueba_lote.db"))
