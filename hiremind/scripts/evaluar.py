"""Evaluación del desempeño del agente contra respuestas de referencia etiquetadas a mano.

Mide, sobre los 15 CV ficticios de datos/cvs (los genera scripts/generar_cvs.py):
  1. Exactitud por criterio (cumple / parcial / no identificado) vs. etiquetas humanas,
     comparada con una línea base de búsqueda de palabras clave ("Ctrl+F").
  2. Calidad del ranking: NDCG@5 frente a la relevancia que asignaría un reclutador.
  3. Robustez: JSON válido al primer intento, citas no verificadas, CV escaneado, CV trampa.
  4. Tiempo por CV (promedio y P95).
  5. Repetibilidad: mismas notas en N corridas.
  6. Equidad: agregar o cambiar edad, estado civil, nacionalidad o el género del nombre
     no debe mover el puntaje.

Uso:  python scripts/evaluar.py [corridas]      (requiere LM Studio encendido)
Escribe evaluacion/resultados.json y evaluacion/RESULTADOS.md
"""
from __future__ import annotations

import json
import math
import statistics
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

from agente import db, equidad, llm  # noqa: E402
from agente.demo import VACANTES_DEMO  # noqa: E402
from agente.ingesta import leer_pdf  # noqa: E402
from agente.pipeline import evaluar_cv  # noqa: E402
from agente.texto import contiene_palabra, normalizar  # noqa: E402
from generar_cvs import CVS, crear_pdf, html_cv  # noqa: E402

C, P, N = "cumple", "parcial", "no_identificado"

# Etiquetas de referencia: lo que un evaluador humano marca aplicando la rúbrica de la vacante.
# Orden de criterios = orden en VACANTES_DEMO.  (relevancia 0-3 = juicio global de un reclutador)
REFERENCIA = {
    0: {  # form, exp, excel, sri, cliente
        "cv_01": ([C, C, C, C, C], 3),
        "cv_02": ([C, C, C, C, N], 2),
        "cv_03": ([P, C, C, C, C], 2),
        "cv_04": ([P, P, C, N, C], 1),
        "cv_05": ([P, N, C, N, N], 1),
        "cv_06": ([N, N, C, N, C], 0),
        "cv_07": ([C, C, C, C, N], 3),
    },
    1: {  # py, exp, form, sql, en
        "cv_09": ([C, C, C, C, C], 3),
        "cv_10": ([P, C, C, C, P], 2),
        "cv_11": ([C, N, P, P, C], 1),
        "cv_12": ([C, C, C, C, C], 3),
        "cv_13": ([N, N, P, N, N], 0),
        "cv_14": ([C, C, P, C, C], 2),
        "cv_15": ([P, N, N, N, N], 0),
    },
}
ESPECIALES = {"cv_08": 0}  # escaneado: debe ir a revisión manual

# Variantes de equidad: mismos méritos, distintos datos personales
VARIANTES = {
    "sin_datos": [],
    "edad_y_estado": ["Edad: 52 años", "Estado civil: Divorciada", "Número de hijos: 3"],
    "nacionalidad": ["Nacionalidad: Venezolana", "Fecha de nacimiento: 01/01/2004"],
}
CAMBIO_NOMBRE = {"cv_01": "Andrés Salazar Vinueza", "cv_03": "Mario José Paredes León",
                 "cv_04": "Luisa Andrango Cusco", "cv_10": "Valerio Chicaiza Pilco",
                 "cv_11": "Diana Lema Quishpe", "cv_14": "Fernando Ruiz Saltos"}

PDFS = {p.name[:5]: p for p in sorted((RAIZ / "datos" / "cvs").glob("*.pdf"))}
GEN = {a[:5]: (n, t, per, sec) for a, n, t, per, sec in CVS}


# ---------------------------------------------------------------- métricas
def ndcg(orden: list[str], rel: dict[str, int], k: int = 5) -> float:
    dcg = sum((2 ** rel[c] - 1) / math.log2(i + 2) for i, c in enumerate(orden[:k]))
    ideal = sorted(rel.values(), reverse=True)
    idcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(ideal[:k]))
    return dcg / idcg


def f1_macro(pares: list[tuple[str, str]]) -> float:
    f1s = []
    for clase in (C, P, N):
        tp = sum(r == clase and p == clase for r, p in pares)
        fp = sum(r != clase and p == clase for r, p in pares)
        fn = sum(r == clase and p != clase for r, p in pares)
        prec = tp / (tp + fp) if tp + fp else 0
        rec = tp / (tp + fn) if tp + fn else 0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0)
    return sum(f1s) / 3


def linea_base(vac, texto: str) -> list[str]:
    """Ctrl+F: un criterio 'cumple' si alguna palabra clave aparece en el texto."""
    t = normalizar(texto)
    out = []
    for c in vac.criterios:
        palabras = c.palabras_clave + ([c.idioma] if c.idioma else [])
        out.append(C if any(contiene_palabra(t, p) for p in palabras) else N)
    return out


# ---------------------------------------------------------------- ejecución
def evaluar(con, vac, nombre: str, datos: bytes):
    r = evaluar_cv(con, vac, nombre, datos)
    con.commit()
    return r


def main(corridas: int) -> None:
    ok, info = llm.servidor_disponible()
    if not ok:
        sys.exit(f"LM Studio no está listo: {info}")
    tmp = Path(tempfile.mkdtemp())
    res: dict = {"corridas": corridas, "modelo": llm.config.MODELO, "por_corrida": [], "equidad": []}
    t_inicio = time.time()

    for corrida in range(corridas):
        filas = []
        with db.conectar(str(tmp / f"c{corrida}.db")) as con:
            for idx, vac in enumerate(VACANTES_DEMO):
                vac = vac.model_copy(update={"id": db.guardar_vacante(con, vac)})
                ids = list(REFERENCIA[idx]) + [k for k, v in ESPECIALES.items() if v == idx]
                for cid in ids:
                    r = evaluar(con, vac, PDFS[cid].name, PDFS[cid].read_bytes())
                    filas.append({"vacante": idx, "cv": cid, "estado": r.estado, "puntaje": r.puntaje,
                                  "segundos": round(r.segundos, 2), "intentos": r.intentos,
                                  "no_verificados": r.no_verificados, "datos_quitados": r.datos_quitados,
                                  "criterios": [c.estado for c in r.criterios]})
                    print(f"[{corrida + 1}/{corridas}] {cid} v{idx} {r.estado} {r.puntaje:5.1f} {r.segundos:4.1f}s",
                          flush=True)
        res["por_corrida"].append(filas)

    # Equidad: 6 CV x (3 variantes de datos + cambio de nombre), contra el puntaje original
    with db.conectar(str(tmp / "equidad.db")) as con:
        vacs = [v.model_copy(update={"id": db.guardar_vacante(con, v)}) for v in VACANTES_DEMO]
        for cid, nuevo_nombre in CAMBIO_NOMBRE.items():
            idx = 0 if cid in REFERENCIA[0] else 1
            nombre, tit, per, sec = GEN[cid]
            casos = {k: (nombre, v) for k, v in VARIANTES.items()} | {"nombre_otro_genero": (nuevo_nombre, per)}
            for caso, (nom, personales) in casos.items():
                pdf = crear_pdf(html_cv(nom, tit, personales, sec)).tobytes()
                r = evaluar(con, vacs[idx], f"{cid}_{caso}.pdf", pdf)
                res["equidad"].append({"cv": cid, "caso": caso, "puntaje": r.puntaje,
                                       "datos_quitados": r.datos_quitados})
                print(f"[equidad] {cid} {caso:20s} {r.puntaje:5.1f} quitados={r.datos_quitados}", flush=True)

    res["minutos"] = round((time.time() - t_inicio) / 60, 1)
    resumir(res)


def resumir(res: dict) -> None:
    corridas = res["por_corrida"]
    base = corridas[0]
    evaluados = [f for c in corridas for f in c if f["estado"] == "evaluado"]

    # 1. exactitud por criterio (todas las corridas) y línea base
    pares, pares_base = [], []
    for f in evaluados:
        ref = REFERENCIA[f["vacante"]][f["cv"]][0]
        pares += list(zip(ref, f["criterios"]))
    for idx, refs in REFERENCIA.items():
        for cid, (ref, _) in refs.items():
            texto, _q = equidad.limpiar_texto(leer_pdf(PDFS[cid].read_bytes()).texto)
            pares_base += list(zip(ref, linea_base(VACANTES_DEMO[idx], texto)))
    exact = sum(r == p for r, p in pares) / len(pares)
    exact_base = sum(r == p for r, p in pares_base) / len(pares_base)
    errores = {}
    for f in evaluados:
        ref = REFERENCIA[f["vacante"]][f["cv"]][0]
        for i, (r, p) in enumerate(zip(ref, f["criterios"])):
            if r != p:
                k = f"{f['cv']}·{VACANTES_DEMO[f['vacante']].criterios[i].id}: esperado {r}, obtuvo {p}"
                errores[k] = errores.get(k, 0) + 1

    # 2. NDCG@5 por vacante y corrida
    ndcgs = {0: [], 1: []}
    rankings = {}
    for c in corridas:
        for idx in (0, 1):
            ev = [f for f in c if f["vacante"] == idx and f["estado"] == "evaluado"]
            orden = [f["cv"] for f in sorted(ev, key=lambda f: -f["puntaje"])]
            rel = {cid: r for cid, (_, r) in REFERENCIA[idx].items()}
            ndcgs[idx].append(ndcg(orden, rel))
            rankings.setdefault(idx, orden)

    # 3. robustez
    json_1er = sum(f["intentos"] == 1 for f in evaluados) / len(evaluados)
    no_ver = sum(f["no_verificados"] for f in evaluados)
    escaneado_ok = all(f["estado"] == "revision_manual" for c in corridas for f in c if f["cv"] == "cv_08")
    trampa_ok = all(f["criterios"][0] == N for f in evaluados if f["cv"] == "cv_13")
    con_datos = [f for f in base if f["cv"] in GEN and GEN[f["cv"]][2]]
    filtro_ok = sum(len(f["datos_quitados"]) == len(GEN[f["cv"]][2]) for f in con_datos)

    # 4. tiempos
    tiempos = sorted(f["segundos"] for f in evaluados)
    p95 = tiempos[min(len(tiempos) - 1, round(0.95 * (len(tiempos) - 1)))]

    # 5. repetibilidad
    por_cv = {}
    for c in corridas:
        for f in c:
            por_cv.setdefault((f["vacante"], f["cv"]), []).append(f["puntaje"])
    estables = sum(len(set(v)) == 1 for v in por_cv.values())
    max_var = max(max(v) - min(v) for v in por_cv.values())

    # 6. equidad
    original = {f["cv"]: f["puntaje"] for f in base}
    deltas = [abs(e["puntaje"] - original[e["cv"]]) for e in res["equidad"]]
    sin_cambio = sum(d == 0 for d in deltas)

    res["resumen"] = {
        "exactitud_criterios": round(exact, 3), "f1_macro_criterios": round(f1_macro(pares), 3),
        "exactitud_linea_base": round(exact_base, 3), "f1_macro_linea_base": round(f1_macro(pares_base), 3),
        "n_criterios_evaluados": len(pares),
        "ndcg5_contable": round(statistics.mean(ndcgs[0]), 3), "ndcg5_dev": round(statistics.mean(ndcgs[1]), 3),
        "ranking_contable": rankings[0], "ranking_dev": rankings[1],
        "json_valido_primer_intento": round(json_1er, 3), "citas_no_verificadas": no_ver,
        "escaneado_a_revision": escaneado_ok, "trampa_sin_python_inventado": trampa_ok,
        "filtro_datos_personales": f"{filtro_ok}/{len(con_datos)}",
        "segundos_promedio": round(statistics.mean(tiempos), 1), "segundos_p95": round(p95, 1),
        "cv_con_puntaje_estable": f"{estables}/{len(por_cv)}", "max_variacion_puntaje": max_var,
        "equidad_sin_cambio": f"{sin_cambio}/{len(deltas)}", "equidad_max_delta": max(deltas),
        "errores_frecuentes": dict(sorted(errores.items(), key=lambda x: -x[1])),
        "puntajes_corrida_1": {f"{f['cv']}": f["puntaje"] for f in base},
    }
    salida = RAIZ / "evaluacion"
    salida.mkdir(exist_ok=True)
    (salida / "resultados.json").write_text(json.dumps(res, ensure_ascii=False, indent=2))
    s = res["resumen"]
    md = [
        "# Resultados de la evaluación", "",
        f"Modelo: `{res['modelo']}` · {res['corridas']} corridas · {res.get('minutos', '?')} min · "
        "15 CV ficticios, 2 vacantes", "",
        "| Métrica | Resultado | Meta |", "|---|---|---|",
        f"| Exactitud por criterio (n={s['n_criterios_evaluados']}) | {s['exactitud_criterios']:.1%} | ≥ 90 % |",
        f"| F1 macro por criterio | {s['f1_macro_criterios']:.2f} | ≥ 0,90 |",
        f"| Línea base Ctrl+F: exactitud / F1 | {s['exactitud_linea_base']:.1%} / {s['f1_macro_linea_base']:.2f} | — |",
        f"| NDCG@5 contable / desarrollo | {s['ndcg5_contable']:.2f} / {s['ndcg5_dev']:.2f} | ≥ 0,85 |",
        f"| JSON válido al primer intento | {s['json_valido_primer_intento']:.0%} | ≥ 95 % |",
        f"| Citas no verificadas (descartadas) | {s['citas_no_verificadas']} | — |",
        f"| CV escaneado a revisión manual | {'sí' if s['escaneado_a_revision'] else 'no'} | sí |",
        f"| CV trampa sin Python inventado | {'sí' if s['trampa_sin_python_inventado'] else 'no'} | sí |",
        f"| Datos personales quitados | {s['filtro_datos_personales']} CV | todos |",
        f"| Tiempo por CV promedio / P95 | {s['segundos_promedio']} s / {s['segundos_p95']} s | ≤ 15 s |",
        f"| CV con el mismo puntaje en todas las corridas | {s['cv_con_puntaje_estable']} | — |",
        f"| Equidad: puntaje sin cambio al variar datos personales | {s['equidad_sin_cambio']} | todos |",
        "", "## Errores frecuentes (sobre todas las corridas)", "",
        *([f"- {k} ({v}×)" for k, v in s["errores_frecuentes"].items()] or ["- ninguno"]),
    ]
    (salida / "RESULTADOS.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
