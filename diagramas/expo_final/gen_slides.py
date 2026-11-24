"""Genera las diapositivas nuevas de la exposición final (HTML 1920x1080 -> PNG 3840x2160).

Estilo: el de la presentación del grupo en Canva (marca A: menta, coral, noche, azul; Bebas Neue + Montserrat).
Los números de resultados salen de hiremind/evaluacion/resultados.json (scripts/evaluar.py).
Los números de pricing salen de PRICING más abajo (supuestos declarados en la diapositiva).

Uso:  python gen_slides.py            -> escribe html/*.html ; luego  node render.mjs  -> png/*.png
"""
from __future__ import annotations

import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
import os
RES = json.loads(Path(os.getenv("RESULTADOS", AQUI.parent.parent / "hiremind" / "evaluacion" / "resultados.json")).read_text())["resumen"]
OUT = AQUI / "html"
OUT.mkdir(exist_ok=True)

NOCHE, MENTA, CORAL, AZUL, AMBAR = "#0A0147", "#2EE5A7", "#FD696E", "#5383FF", "#FFB547"


def pct(x: float) -> str:
    return f"{x * 100:.1f}".replace(".", ",").replace(",0", "") + " %"


def dec(x: float, n: int = 2) -> str:
    return f"{x:.{n}f}".replace(".", ",")


def money(x: float) -> str:
    return f"${x:,.0f}".replace(",", " ")


CSS = f"""
@font-face {{ font-family: Bebas; src: url(../fuentes/bebas-neue-latin-400-normal.woff2); }}
@font-face {{ font-family: Mont; src: url(../fuentes/montserrat-latin-wght-normal.woff2); font-weight: 100 900; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 1920px; height: 1080px; overflow: hidden; }}
body {{ font-family: Mont, sans-serif; color: {NOCHE}; position: relative; }}
.menta {{ background: {MENTA}; }} .coral {{ background: {CORAL}; }} .noche {{ background: {NOCHE}; color: #fff; }}
.blanco {{ background: #fff; }} .azul {{ background: {AZUL}; }}
.t {{ font-family: Bebas; font-size: 112px; line-height: .92; letter-spacing: .5px; }}
.st {{ font-size: 30px; font-weight: 600; margin-top: 10px; opacity: .85; }}
.cab {{ position: absolute; left: 110px; top: 78px; right: 110px; }}
.deco {{ position: absolute; }}
.card {{ background: #fff; color: {NOCHE}; border: 4px solid {NOCHE}; box-shadow: 10px 10px 0 {NOCHE}; }}
.noche .card {{ box-shadow: 10px 10px 0 {MENTA}; border-color: #fff; }}
.big {{ font-family: Bebas; line-height: .9; }}
.chip {{ display: inline-block; font-weight: 800; font-size: 20px; text-transform: uppercase; letter-spacing: 1.5px;
        padding: 6px 14px; border: 3px solid {NOCHE}; }}
.lbl {{ font-size: 20px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; }}
.p {{ font-size: 26px; font-weight: 500; line-height: 1.35; }}
.fuente {{ position: absolute; left: 110px; bottom: 34px; font-size: 18px; font-weight: 600; opacity: .7; }}
"""

# decoraciones como en el deck: barras y semicírculos en los bordes
DECOS = {
    "menta": f'<div class="deco" style="left:0;top:0;width:330px;height:26px;background:{NOCHE}"></div>'
             f'<div class="deco" style="right:120px;bottom:0;width:260px;height:38px;background:{AZUL}"></div>'
             f'<div class="deco" style="right:-90px;top:-90px;width:220px;height:220px;border-radius:50%;border:34px solid {CORAL}"></div>',
    "coral": f'<div class="deco" style="right:0;top:0;width:300px;height:26px;background:{NOCHE}"></div>'
             f'<div class="deco" style="left:140px;bottom:0;width:240px;height:38px;background:{AZUL}"></div>'
             f'<div class="deco" style="left:-100px;bottom:-100px;width:230px;height:230px;border-radius:50%;border:34px solid #fff"></div>',
    "noche": f'<div class="deco" style="left:0;top:0;width:300px;height:26px;background:{CORAL}"></div>'
             f'<div class="deco" style="right:140px;bottom:0;width:240px;height:38px;background:{MENTA}"></div>'
             f'<div class="deco" style="right:-100px;top:-100px;width:230px;height:230px;border-radius:50%;border:34px solid {AZUL}"></div>',
    "blanco": f'<div class="deco" style="left:0;top:0;width:330px;height:26px;background:{MENTA}"></div>'
              f'<div class="deco" style="right:120px;bottom:0;width:260px;height:38px;background:{CORAL}"></div>'
              f'<div class="deco" style="right:-90px;top:-90px;width:220px;height:220px;border-radius:50%;border:34px solid {AZUL}"></div>',
}


def slide(nombre: str, fondo: str, titulo: str, sub: str, cuerpo: str, fuente: str = "") -> None:
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body class="{fondo}">{DECOS[fondo]}
<div class="cab"><div class="t">{titulo}</div>{f'<div class="st">{sub}</div>' if sub else ''}</div>
{cuerpo}
{f'<div class="fuente">{fuente}</div>' if fuente else ''}
</body></html>"""
    (OUT / f"{nombre}.html").write_text(html)


def box(x, y, w, h, inner, extra=""):
    return f'<div class="card" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra}">{inner}</div>'


# =====================================================================================
# 07 · Herramientas (reemplaza la de Streamlit)
capas = [
    ("Interfaz", MENTA, [("React 19 + Vite", "pantallas: panel, vacante, CV, ranking"), ("Tailwind 4", "marca y temas claro/oscuro"),
                         ("TanStack Query", "datos del servidor en vivo")]),
    ("Servicio", AZUL, [("FastAPI", "API REST local · puerto 8000"), ("Pydantic", "esquema JSON estricto"),
                        ("pytest", "pruebas de reglas y API")]),
    ("Agente", CORAL, [("Python", "orquesta y puntúa Σ wᵢ·sᵢ"), ("PyMuPDF", "lee el texto del PDF"),
                       ("OpenAI SDK", "cliente del modelo local")]),
    ("Modelo y datos", AMBAR, [("LM Studio", "servidor local OpenAI-compatible"), ("Qwen3-4B-Instruct", "GGUF Q4 · 2,5 GB · 8k"),
                               ("SQLite", "vacantes, CV, evidencias")]),
]
filas = ""
for i, (capa, color, items) in enumerate(capas):
    y = 290 + i * 172
    filas += f'<div style="position:absolute;left:110px;top:{y}px;width:250px;height:140px;background:{color};border:4px solid #fff;display:flex;align-items:center;justify-content:center"><span class="big" style="font-size:52px;color:{NOCHE};text-align:center">{capa}</span></div>'
    for j, (n, d) in enumerate(items):
        filas += box(400 + j * 470, y, 440, 140,
                     f'<div style="padding:22px 26px"><div style="font-size:34px;font-weight:800">{n}</div><div style="font-size:23px;font-weight:500;margin-top:6px;opacity:.8">{d}</div></div>')
slide("07_herramientas", "noche", "Herramientas y su rol", "Cuatro capas, todo corre en el equipo de la PYME · 100 % código abierto", filas,
      "Cambio respecto al entregable 1: la interfaz pasó de Streamlit a React + FastAPI (más rápida y con marca propia).")

# =====================================================================================
# 08 · Flujo de trabajo + principios
pasos = [("1", "Iniciar LM Studio", "carga Qwen3-4B"), ("2", "Crear vacante", "criterios y pesos = 100 %"),
         ("3", "Subir CV", "varios PDF a la vez"), ("4", "Leer y limpiar", "PyMuPDF + quitar datos personales"),
         ("5", "Extraer a JSON", "el LLM, con citas textuales"), ("6", "Verificar y puntuar", "Python: Σ wᵢ·sᵢ"),
         ("7", "Revisar ranking", "la persona decide")]
c = ""
for i, (n, t, d) in enumerate(pasos):
    x = 110 + i * 243
    color = CORAL if i in (0, 1, 2, 6) else MENTA
    c += f'<div style="position:absolute;left:{x}px;top:300px;width:215px">' \
         f'<div style="width:86px;height:86px;background:{color};border:4px solid {NOCHE};display:flex;align-items:center;justify-content:center" class="big"><span style="font-size:64px">{n}</span></div>' \
         f'<div style="font-size:28px;font-weight:800;margin-top:18px;line-height:1.1">{t}</div><div style="font-size:21px;font-weight:500;margin-top:8px">{d}</div></div>'
    if i < 6:
        c += f'<div style="position:absolute;left:{x + 100}px;top:338px;width:126px;height:6px;background:{NOCHE}"></div>'
c += f'<div style="position:absolute;left:110px;top:560px;font-size:22px;font-weight:700"><span style="display:inline-block;width:22px;height:22px;background:{CORAL};border:3px solid {NOCHE};vertical-align:-4px"></span> reclutador &nbsp;&nbsp; <span style="display:inline-block;width:22px;height:22px;background:{MENTA};border:3px solid {NOCHE};vertical-align:-4px"></span> agente</div>'
principios = [("Sin datos sensibles", "edad, estado civil, nacionalidad, foto: se quitan antes del modelo"),
              ("Evidencia verificable", "cada dato trae una cita; si no está en el CV, no cuenta"),
              ("El LLM no pone la nota", "extrae y redacta; Python aplica reglas fijas"),
              ("Decisión humana", "nadie se descarta; la persona corrige y decide")]
for i, (t, d) in enumerate(principios):
    c += box(110 + i * 432, 650, 400, 300, f'<div style="padding:28px"><div class="lbl" style="color:{CORAL}">Principio {i + 1}</div><div style="font-size:34px;font-weight:800;margin-top:10px;line-height:1.1">{t}</div><div style="font-size:23px;font-weight:500;margin-top:14px;line-height:1.35">{d}</div></div>')
slide("08_flujo", "menta", "Flujo de trabajo y evaluación responsable", "", c)

# =====================================================================================
# 10 · Resultados: tablero contra las metas
kpis = [
    ("Exactitud por criterio", pct(RES["exactitud_criterios"]), "meta ≥ 90 %", RES["exactitud_criterios"] >= .9),
    ("F1 macro", dec(RES["f1_macro_criterios"]), "meta ≥ 0,90", RES["f1_macro_criterios"] >= .9),
    ("NDCG@5 (promedio)", dec((RES["ndcg5_contable"] + RES["ndcg5_dev"]) / 2), "meta ≥ 0,85", (RES["ndcg5_contable"] + RES["ndcg5_dev"]) / 2 >= .85),
    ("JSON válido (1.er intento)", pct(RES["json_valido_primer_intento"]), "meta ≥ 95 %", RES["json_valido_primer_intento"] >= .95),
    ("Tiempo por CV (P95)", dec(RES["segundos_p95"], 1) + " s", f"promedio {dec(RES['segundos_promedio'], 1)} s · meta ≤ 15 s", RES["segundos_p95"] <= 15),
    ("Equidad", RES["equidad_sin_cambio"].replace("/", " de "), "variantes sin cambio de puntaje", RES["equidad_sin_cambio"].split("/")[0] == RES["equidad_sin_cambio"].split("/")[1]),
]
c = ""
for i, (n, v, m, ok) in enumerate(kpis):
    x, y = 110 + (i % 3) * 580, 300 + (i // 3) * 340
    sello = f'<div style="position:absolute;right:22px;top:22px;background:{MENTA if ok else AMBAR};border:3px solid {NOCHE};font-weight:800;font-size:20px;padding:4px 12px">{"CUMPLE" if ok else "CERCA"}</div>'
    c += box(x, y, 540, 300, f'{sello}<div style="padding:30px 32px"><div class="lbl" style="padding-right:130px">{n}</div><div class="big" style="font-size:150px;margin-top:18px">{v}</div><div style="font-size:24px;font-weight:600;margin-top:4px">{m}</div></div>', "position:absolute")
slide("10_resultados", "coral", "Resultados de la evaluación",
      f"{RES['n_criterios_evaluados']} criterios evaluados · 14 CV × 3 corridas · 2 vacantes · Qwen3-4B en GPU de 8 GB", c,
      "Referencia etiquetada a mano por el equipo · script reproducible: hiremind/scripts/evaluar.py")

# =====================================================================================
# 11 · Agente vs. búsqueda de palabras + NDCG
def barra(y, etiqueta, valor, color, txt):
    w = int(860 * valor)
    return (f'<div style="position:absolute;left:150px;top:{y}px;font-size:24px;font-weight:700">{etiqueta}</div>'
            f'<div style="position:absolute;left:150px;top:{y + 38}px;width:860px;height:70px;border:4px solid {NOCHE};background:#fff"></div>'
            f'<div style="position:absolute;left:150px;top:{y + 38}px;width:{w}px;height:70px;border:4px solid {NOCHE};background:{color}"></div>'
            f'<div class="big" style="position:absolute;left:{150 + w + 18}px;top:{y + 36}px;font-size:76px">{txt}</div>')


c = f'<div class="lbl" style="position:absolute;left:150px;top:290px">¿Cuántos criterios clasifica bien?</div>'
c += barra(340, "HireMind (LLM + verificación + reglas)", RES["exactitud_criterios"], MENTA, pct(RES["exactitud_criterios"]))
c += barra(480, "Búsqueda de palabras clave (Ctrl+F)", RES["exactitud_linea_base"], "#C9C6E0", pct(RES["exactitud_linea_base"]))
c += f'<div style="position:absolute;left:150px;top:630px;width:900px" class="p">La búsqueda no distingue <b>experiencia de proyecto</b>, ni <b>carrera en curso de título</b>, ni cuenta <b>años</b>. F1: <b>{dec(RES["f1_macro_criterios"])}</b> vs <b>{dec(RES["f1_macro_linea_base"])}</b>.</div>'
for i, (vac, v) in enumerate([("Asistente contable", RES["ndcg5_contable"]), ("Desarrollador junior", RES["ndcg5_dev"])]):
    x = 1240 + i * 300
    h = int(380 * v)
    c += (f'<div style="position:absolute;left:{x}px;top:{850 - h}px;width:200px;height:{h}px;background:{AZUL if i else MENTA};border:4px solid {NOCHE}"></div>'
          f'<div class="big" style="position:absolute;left:{x}px;top:{760 - h}px;width:200px;text-align:center;font-size:84px">{dec(v)}</div>'
          f'<div style="position:absolute;left:{x - 20}px;top:868px;width:240px;text-align:center;font-size:22px;font-weight:700">{vac}</div>')
c += f'<div style="position:absolute;left:1200px;top:{850 - int(380 * .85)}px;width:580px;border-top:5px dashed {CORAL}"></div><div style="position:absolute;left:1690px;top:{850 - int(380 * .85) + 10}px;font-weight:800;font-size:20px;color:{CORAL};background:#fff;padding:2px 8px;border:2px solid {CORAL}">META 0,85</div>'
c += f'<div class="lbl" style="position:absolute;left:1240px;top:290px">Calidad del ranking · NDCG@5</div>'
c += f'<div style="position:absolute;left:1200px;top:850px;width:600px;height:0px;background:{NOCHE}"></div>'
c += f'<div style="position:absolute;left:1200px;top:930px;width:620px;font-size:22px;font-weight:600">1,00 = el top 5 sale en el mismo orden que el del reclutador.</div>'
slide("11_exactitud", "blanco", "Mejor que buscar palabras", "Mismo CV, misma rúbrica: lo que agrega el agente", c)

# =====================================================================================
# 12 · Equidad y robustez
eq_ok, eq_n = map(int, RES["equidad_sin_cambio"].split("/"))
puntos = "".join(f'<div style="width:58px;height:58px;border:4px solid {NOCHE};background:{MENTA if i < eq_ok else CORAL}"></div>' for i in range(eq_n))
c = box(110, 290, 860, 640, f'<div style="padding:34px 38px"><div class="lbl">Prueba de equidad</div>'
        f'<div style="font-size:30px;font-weight:700;margin-top:12px;line-height:1.25">6 CV reales del set, cada uno con 4 variantes:<br>sin datos · edad y estado civil · otra nacionalidad · nombre del otro género</div>'
        f'<div style="display:grid;grid-template-columns:repeat(8,58px);gap:14px;margin-top:34px">{puntos}</div>'
        f'<div class="big" style="font-size:120px;margin-top:30px">{eq_ok} de {eq_n}</div><div style="font-size:26px;font-weight:600">variantes con el <b>mismo puntaje</b> que el CV original (máx. diferencia: {dec(RES["equidad_max_delta"], 1)} pts)</div></div>')
rob = [("CV escaneado (solo imagen)", "va a revisión manual" if RES["escaneado_a_revision"] else "NO fue a revisión", RES["escaneado_a_revision"]),
       ("CV trampa: diseñador sin Python", "no se inventó Python" if RES["trampa_sin_python_inventado"] else "inventó Python", RES["trampa_sin_python_inventado"]),
       ("Datos personales detectados", RES["filtro_datos_personales"].replace("/", " de ") + " CV limpiados", True),
       ("Repetibilidad en 3 corridas", RES["cv_con_puntaje_estable"].replace("/", " de ") + " CV con igual puntaje", RES["cv_con_puntaje_estable"].split("/")[0] == RES["cv_con_puntaje_estable"].split("/")[1]),
       ("Citas inventadas por el modelo", f'{RES["citas_no_verificadas"]} detectadas y descartadas', True)]
for i, (t, v, ok) in enumerate(rob):
    c += box(1030, 290 + i * 130, 780, 108, f'<div style="display:flex;align-items:center;height:100%;padding:0 26px;gap:22px"><div style="width:56px;height:56px;flex:none;background:{MENTA if ok else AMBAR};border:4px solid {NOCHE};display:flex;align-items:center;justify-content:center;font-size:36px;font-weight:900">{"✓" if ok else "!"}</div><div><div style="font-size:21px;font-weight:700;opacity:.75">{t}</div><div style="font-size:30px;font-weight:800">{v}</div></div></div>')
slide("12_equidad", "menta", "Equidad y robustez", "", c)

# =====================================================================================
# 13 · La solución implementada (capturas)
caps = [("panel", "Panel: procesos, tiempos y distribución"), ("ranking", "Ranking con justificación y evidencia"),
        ("editor", "Vacante: criterios y pesos"), ("subir", "Carga de CV en lote")]
c = ""
for i, (f, t) in enumerate(caps):
    x, y = 110 + (i % 2) * 860, 270 + (i // 2) * 400
    c += (f'<div style="position:absolute;left:{x}px;top:{y}px;width:820px;height:340px;border:4px solid #fff;box-shadow:10px 10px 0 {MENTA};overflow:hidden;background:#fff">'
          f'<img src="../capturas/{f}.png" style="width:820px;display:block"></div>'
          f'<div style="position:absolute;left:{x}px;top:{y + 350}px;font-size:22px;font-weight:700;color:#fff">{t}</div>')
slide("13_app", "noche", "La solución implementada", "Aplicación web local: React + FastAPI + agente en Python · demo en vivo", c)

# =====================================================================================
# 14 · Limitaciones y consideraciones futuras
lim = [("Solo PDF con texto", "los escaneados van a revisión manual (no hay OCR)"),
       ("Rúbrica por palabras clave", "sinónimos no previstos (p. ej. «contables») no cuentan"),
       ("Modelo pequeño (4B)", "necesita 16 GB de RAM; con CV largos o desordenados baja la exactitud"),
       ("Evaluación acotada", "15 CV ficticios y 2 vacantes; falta validar con CV reales de PYMEs"),
       ("Cupos de licencia", "la app aún no limita vacantes ni CV por plan")]
fut = [("Corto plazo", "OCR local (Tesseract) · sinónimos con embeddings"),
       ("Mediano plazo", "Qwen 7B/8B en equipos con más memoria · cupos y licencias"),
       ("Largo plazo", "piloto con 3 PYMEs · nube opcional para campañas masivas")]
c = box(110, 290, 900, 700, '<div style="padding:34px 38px"><div class="chip" style="background:#FFE1E2">Limitaciones técnicas</div>' + "".join(
    f'<div style="margin-top:26px;display:flex;gap:18px"><div style="width:18px;height:18px;flex:none;margin-top:9px;background:{CORAL};border:3px solid {NOCHE}"></div><div><div style="font-size:29px;font-weight:800">{t}</div><div style="font-size:22px;font-weight:500;margin-top:2px">{d}</div></div></div>'
    for t, d in lim) + "</div>")
c += f'<div class="lbl" style="position:absolute;left:1090px;top:290px;color:#fff">Consideraciones futuras</div>'
for i, (t, d) in enumerate(fut):
    y = 350 + i * 215
    c += (f'<div style="position:absolute;left:1090px;top:{y}px;width:26px;height:26px;background:{MENTA};border:4px solid {NOCHE}"></div>'
          + (f'<div style="position:absolute;left:1100px;top:{y + 26}px;width:6px;height:190px;background:{NOCHE}"></div>' if i < 2 else "")
          + box(1150, y - 14, 660, 170, f'<div style="padding:24px 28px"><div class="lbl" style="color:{AZUL}">{t}</div><div style="font-size:28px;font-weight:700;margin-top:10px;line-height:1.25">{d}</div></div>'))
slide("14_limitaciones", "coral", "Limitaciones y futuro", "", c)

# =====================================================================================
# 15 · Modelo de negocio híbrido (escalera)
esc = [("Licencia base perpetua", "$299", "pago único", "1 equipo · 3 vacantes activas · 300 CV/año · sin internet", MENTA, 0),
       ("Plan Crecimiento", "$149", "por año", "12 vacantes · 1 500 CV/año · 3 equipos · modelo actualizado", AZUL, 1),
       ("Plan Escala", "$299", "por año", "sin límite local · 5 equipos · nube opcional · soporte prioritario", CORAL, 2)]
c = ""
for t, p, m, d, col, i in esc:
    x, h = 110 + i * 590, 330 + i * 120
    c += (f'<div style="position:absolute;left:{x}px;bottom:110px;width:560px;height:{h}px;background:{col};border:4px solid {NOCHE};box-shadow:10px 10px 0 {NOCHE};padding:30px 32px">'
          f'<div class="lbl">{"Paso " + str(i + 1)}</div><div style="font-size:36px;font-weight:800;margin-top:6px">{t}</div>'
          f'<div class="big" style="font-size:130px;margin-top:6px">{p}<span style="font-family:Mont;font-size:28px;font-weight:700"> {m}</span></div>'
          f'<div style="font-size:24px;font-weight:600;line-height:1.3">{d}</div></div>')
c += f'<div style="position:absolute;left:110px;top:300px;width:540px" class="p"><b>Compra hoy, escala cuando crezcas.</b><br>Mientras el volumen sea bajo, el costo mensual es <b>$0</b>. La suscripción anual se activa solo si la PYME crece.</div>'
slide("15_modelo", "menta", "Modelo de negocio híbrido", "Licencia perpetua base + expansiones anuales por suscripción", c)

# =====================================================================================
# 16 · Esquema de ingresos en el tiempo (un cliente que crece)
anios = [("Día 0", [("Licencia base", 299, MENTA), ("Setup remoto", 75, AZUL)]),
         ("Año 1", [("Soporte puntual", 85, AMBAR)]),
         ("Año 2", [("Plan Crecimiento", 149, CORAL)]),
         ("Año 3", [("Plan Crecimiento", 149, CORAL), ("Capacitación", 40, AMBAR)])]
c = f'<div style="position:absolute;left:110px;top:880px;width:1700px;height:6px;background:#fff"></div>'
for i, (a, partes) in enumerate(anios):
    x, y0 = 180 + i * 420, 880
    for n, v, col in partes:
        h = int(v * 1.5)
        y0 -= h
        c += f'<div style="position:absolute;left:{x}px;top:{y0}px;width:240px;height:{h}px;background:{col};border:4px solid {NOCHE};display:flex;align-items:center;justify-content:center;flex-direction:column"><span style="font-weight:800;font-size:21px;color:{NOCHE}">{n}</span><span class="big" style="font-size:46px;color:{NOCHE}">${v}</span></div>'
    c += f'<div class="big" style="position:absolute;left:{x}px;top:900px;width:240px;text-align:center;font-size:52px;color:#fff">{a}</div>'
total = 299 + 75 + 85 + 149 + 149 + 40
c += f'<div style="position:absolute;right:110px;top:290px;text-align:right;color:#fff"><div class="lbl" style="color:{MENTA}">Valor del cliente en 3 años</div><div class="big" style="font-size:150px">${total}</div><div style="font-size:24px;font-weight:600">escenario: PYME que crece en el año 2</div></div>'
slide("16_ingresos", "noche", "Esquema de ingresos", "Un pago fuerte al inicio, luego ingresos anuales solo si el cliente crece", c)

# =====================================================================================
# 18 · Estructura tarifaria (precios)
tar = [("Licencia base", "$299", "pago único", MENTA), ("Setup remoto", "$75", "obligatorio", MENTA),
       ("Setup presencial", "$120", "opcional", "#fff"), ("Plan Crecimiento", "$149", "por año", AZUL),
       ("Plan Escala", "$299", "por año", CORAL), ("Soporte puntual", "$85", "bajo demanda", "#fff")]
c = ""
for i, (n, p, m, col) in enumerate(tar):
    x = 110 + i * 290
    c += box(x, 300, 260, 360, f'<div style="background:{col};border-bottom:4px solid {NOCHE};padding:20px 18px;font-size:25px;font-weight:800;height:100px">{n}</div><div style="padding:22px 18px"><div class="big" style="font-size:104px">{p}</div><div style="font-size:22px;font-weight:700">{m}</div></div>')
c += box(110, 740, 1700, 190, f'<div style="display:flex;align-items:center;height:100%;padding:0 46px;gap:46px"><div class="lbl" style="width:170px;flex:none">Ticket de entrada</div><div class="big" style="font-size:100px;white-space:nowrap;flex:none">$299 + $75 = <span style="background:{MENTA};padding:0 18px">$374</span></div><div style="font-size:23px;font-weight:600;line-height:1.35">pago único · tarjeta diferida 3–6 meses sin intereses o 50 % / 50 %</div></div>')
slide("18_tarifas", "blanco", "Estructura tarifaria", "Precios en USD", c)

# =====================================================================================
# 19 · Cálculo del precio (costo + punto de equilibrio)
P = {
    "dev_horas": 480, "dev_tarifa": 6, "amort_anios": 3,
    "setup_horas": 3, "tarifa_tecnico": 10, "comision": 0.06, "garantia_horas": 1,
    "fijos": [("Marketing digital", 1200), ("Landing y dominio", 120), ("Contabilidad (RIMPE)", 360), ("Equipo de pruebas (depreciación)", 300)],
}
inv = P["dev_horas"] * P["dev_tarifa"]
var = P["setup_horas"] * P["tarifa_tecnico"] + P["comision"] * 374 + P["garantia_horas"] * P["tarifa_tecnico"]
contrib = 374 - var
fijos = sum(v for _, v in P["fijos"])
amort = inv / P["amort_anios"]
equilibrio = (fijos + amort) / contrib
filas = [("Precio de entrada (licencia + setup)", 374, NOCHE),
         (f"Setup: {P['setup_horas']} h × ${P['tarifa_tecnico']}/h", -P["setup_horas"] * P["tarifa_tecnico"], CORAL),
         (f"Comisión de cobro {int(P['comision'] * 100)} %", -P["comision"] * 374, CORAL),
         (f"Garantía: {P['garantia_horas']} h de soporte", -P["garantia_horas"] * P["tarifa_tecnico"], CORAL),
         ("Margen de contribución por cliente", contrib, AZUL)]
c = '<div style="position:absolute;left:110px;top:290px;width:900px">'
for n, v, col in filas:
    w = int(abs(v) / 374 * 520)
    c += f'<div style="display:flex;align-items:center;height:86px;border-bottom:3px solid {NOCHE}"><div style="width:380px;font-size:23px;font-weight:700">{n}</div><div style="width:{w}px;height:46px;background:{col};border:3px solid {NOCHE}"></div><div class="big" style="font-size:52px;margin-left:16px">{"−" if v < 0 else ""}${abs(v):.0f}</div></div>'
c += "</div>"
c += box(1080, 290, 730, 380, '<div style="padding:30px 34px"><div class="lbl">Costos fijos al año</div>' + "".join(
    f'<div style="display:flex;justify-content:space-between;font-size:24px;font-weight:600;margin-top:12px"><span>{n}</span><b>${v:,}</b></div>' for n, v in P["fijos"])
    + f'<div style="display:flex;justify-content:space-between;font-size:24px;font-weight:600;margin-top:12px"><span>Desarrollo {P["dev_horas"]} h × ${P["dev_tarifa"]} ÷ {P["amort_anios"]} años</span><b>${amort:,.0f}</b></div>'
    + f'<div style="display:flex;justify-content:space-between;font-size:28px;font-weight:800;margin-top:18px;border-top:4px solid {NOCHE};padding-top:12px"><span>Total a cubrir</span><span>${fijos + amort:,.0f}</span></div></div>')
c += box(1080, 720, 730, 220, f'<div style="display:flex;align-items:center;height:100%;padding:0 34px;gap:28px;background:{MENTA}"><div class="big" style="font-size:150px">{equilibrio:.0f}→{int(equilibrio) + 1}</div><div style="font-size:26px;font-weight:700;line-height:1.3">clientes al año para el punto de equilibrio<br><span style="font-weight:500;font-size:21px">${fijos + amort:,.0f} ÷ ${contrib:.0f} por cliente</span></div></div>')
slide("19_calculo", "menta", "Cálculo del precio", "Costo por cliente, margen y punto de equilibrio (año 1)", c,
      "Supuestos del equipo: tarifa de practicante $6/h para el desarrollo; técnico $10/h; comisión de tarjeta diferida 6 %.")

# =====================================================================================
# 20 · Valor para el cliente (3 años, 3 contrataciones al año)
salario = 600
agencia = 0.75 * salario * 3 * 3
portales = 60 * 3 * 3
barras = [("Agencia de reclutamiento", agencia, "#C9C6E0", f"75 % de un sueldo de ${salario} × 9 procesos"),
          ("Portales de empleo (anuncios)", portales, "#C9C6E0", "$60 por anuncio × 9"),
          ("HireMind + Plan Crecimiento", 374 + 149 * 2, AZUL, "$374 + $149 en los años 2 y 3"),
          ("HireMind licencia base", 374, MENTA, "$374 una vez")]
c = ""
mx = max(v for _, v, _, _ in barras)
for i, (n, v, col, d) in enumerate(barras):
    y = 300 + i * 160
    w = int(v / mx * 1000)
    c += (f'<div style="position:absolute;left:110px;top:{y}px;width:440px"><div style="font-size:26px;font-weight:800">{n}</div><div style="font-size:20px;font-weight:500;margin-top:4px">{d}</div></div>'
          f'<div style="position:absolute;left:580px;top:{y}px;width:{w}px;height:100px;background:{col};border:4px solid {NOCHE}"></div>'
          f'<div class="big" style="position:absolute;left:{600 + w}px;top:{y + 6}px;font-size:96px">${v:,.0f}</div>')
ahorro = agencia - (374 + 149 * 2)
c += f'<div style="position:absolute;left:110px;top:950px" class="p">Frente a una agencia, la PYME ahorra <b>${ahorro:,.0f}</b> en 3 años; la licencia se paga con <b>la primera contratación</b> que no se terceriza.</div>'
slide("20_valor", "blanco", "Valor para el cliente", "Costo de seleccionar personal en 3 años · PYME con 3 contrataciones al año", c,
      "Agencias: 50–100 % del primer sueldo; portales: $40–80 por anuncio (Modelo de Negocio Híbrido, 2026). Sueldo de referencia $600.")

# =====================================================================================
# 21 · Riesgos (matriz probabilidad x impacto)
riesgos = [("R1", "Sesgo o error en el ranking", 2, 3), ("R2", "Equipo sin 16 GB de RAM", 3, 2), ("R3", "CV escaneados o con formato raro", 3, 1),
           ("R4", "Fuga de datos personales", 1, 3), ("R5", "Modelo desactualizado", 2, 1), ("R6", "Baja adopción / precio", 2, 2)]
mit = {"R1": "Reglas fijas, evidencia citada, filtro de datos y decisión humana",
       "R2": "Auditoría de hardware en el setup; modelo 4B cuantizado",
       "R3": "Revisión manual automática; OCR en la hoja de ruta",
       "R4": "Todo local: SQLite y LM Studio sin nube (LOPDP)",
       "R5": "Actualización anual en los planes; cambio de modelo sin tocar el código",
       "R6": "Demo con CV reales del cliente; pago diferido"}
color_celda = {2: MENTA, 3: AMBAR, 4: AMBAR, 5: CORAL, 6: CORAL, 1: MENTA, 9: CORAL}
c = ""
for p in (1, 2, 3):
    for im in (1, 2, 3):
        x, y = 230 + (im - 1) * 200, 300 + (3 - p) * 200
        col = color_celda.get(p * im, CORAL)
        c += f'<div style="position:absolute;left:{x}px;top:{y}px;width:200px;height:200px;background:{col};border:3px solid {NOCHE};opacity:.9"></div>'
for k, (rid, n, p, im) in enumerate(riesgos):
    mismos = [r for r in riesgos if r[2] == p and r[3] == im]
    off = mismos.index((rid, n, p, im)) * 70
    x, y = 230 + (im - 1) * 200 + 30 + off, 300 + (3 - p) * 200 + 60
    c += f'<div class="big" style="position:absolute;left:{x}px;top:{y}px;width:70px;height:70px;background:#fff;border:4px solid {NOCHE};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:40px">{rid}</div>'
c += f'<div class="lbl" style="position:absolute;left:230px;top:915px;width:600px;text-align:center">Impacto →</div><div class="lbl" style="position:absolute;left:160px;top:300px;height:600px;writing-mode:vertical-rl;transform:rotate(180deg);text-align:center">Probabilidad →</div>'
c += '<div style="position:absolute;left:900px;top:290px;width:920px">' + "".join(
    f'<div style="display:flex;gap:18px;padding:14px 0;border-bottom:3px solid {NOCHE}"><div class="big" style="font-size:44px;width:64px">{rid}</div><div><div style="font-size:24px;font-weight:800">{n}</div><div style="font-size:21px;font-weight:500">{mit[rid]}</div></div></div>'
    for rid, n, _, _ in riesgos) + "</div>"
slide("21_riesgos", "blanco", "Análisis de riesgos", "Probabilidad × impacto y su mitigación", c)

# =====================================================================================
# 22 · Sostenibilidad y mantenimiento
sost = [("Económica", "cliente rentable desde el día 0 ($312 de margen); ingresos recurrentes con las expansiones; punto de equilibrio en ~10 clientes al año", MENTA),
        ("Técnica", "código abierto y modular: cambiar de modelo es cambiar un nombre en la configuración; pruebas automáticas de reglas y API", AZUL),
        ("Ambiental y social", "corre en el equipo que ya existe (sin servidores ni GPU dedicada); decisiones sin sesgo por edad, género o nacionalidad", AMBAR)]
c = ""
for i, (t, d, col) in enumerate(sost):
    c += box(110 + i * 580, 290, 540, 330, f'<div style="background:{col};border-bottom:4px solid {NOCHE};padding:18px 26px" class="big"><span style="font-size:56px">{t}</span></div><div style="padding:22px 26px;font-size:24px;font-weight:600;line-height:1.35">{d}</div>')
mant = [("Preventivo", "anual", "actualizar modelo, respaldo de SQLite, revisar rúbricas"),
        ("Correctivo", "bajo demanda", "fallas, cambio de equipo, base dañada ($85)"),
        ("Evolutivo", "por versión", "OCR, sinónimos, nuevos idiomas"),
        ("Monitoreo", "continuo", "tiempo por CV, CV en revisión manual, correcciones del reclutador")]
c += '<div class="lbl" style="position:absolute;left:110px;top:670px">Plan de mantenimiento</div>'
for i, (t, f, d) in enumerate(mant):
    c += box(110 + i * 432, 715, 400, 220, f'<div style="padding:22px 24px"><div style="font-size:30px;font-weight:800">{t}</div><div class="chip" style="font-size:16px;margin-top:8px;background:{MENTA}">{f}</div><div style="font-size:21px;font-weight:500;margin-top:12px;line-height:1.3">{d}</div></div>')
slide("22_sostenibilidad", "coral", "Sostenibilidad y mantenimiento", "", c)

# =====================================================================================
# 23 · Conclusiones
concl = [(pct(RES["exactitud_criterios"]), "de los criterios bien clasificados con un modelo de 4B que corre en una laptop"),
         (dec(RES["segundos_promedio"], 1) + " s", "por hoja de vida: 60 CV en menos de 10 minutos, sin internet"),
         (RES["equidad_sin_cambio"].replace("/", " de "), "variantes de datos personales sin cambio de puntaje"),
         ("$374", "ticket de entrada: menos que una sola contratación por agencia")]
c = ""
for i, (v, d) in enumerate(concl):
    x, y = 110 + (i % 2) * 870, 290 + (i // 2) * 330
    c += box(x, y, 830, 290, f'<div style="padding:30px 36px"><div class="big" style="font-size:150px;color:{NOCHE}">{v}</div><div style="font-size:28px;font-weight:700;line-height:1.3;margin-top:4px">{d}</div></div>')
c += f'<div style="position:absolute;left:110px;top:960px;color:#fff" class="p"><b>Separar tareas funciona:</b> el LLM lee y redacta, Python decide con reglas fijas y la persona tiene la última palabra.</div>'
slide("23_conclusiones", "noche", "Conclusiones", "", c)

# =====================================================================================
# 24 · Recomendaciones
rec = [("Para las PYMEs", ["Definir criterios y pesos antes de abrir la vacante", "Revisar siempre el top 5 y corregir lo que falte", "Pedir CV en PDF digital, no escaneado"]),
       ("Para el producto", ["Piloto con 3 PYMEs y CV reales antes de vender", "Agregar OCR y sinónimos con embeddings", "Implementar los cupos de cada plan"]),
       ("Para el negocio", ["Vender con una demo sobre los CV del propio cliente", "Ofrecer pago diferido para bajar la barrera", "Medir la conversión de base a Crecimiento"])]
c = ""
cols = [MENTA, AZUL, CORAL]
for i, (t, items) in enumerate(rec):
    c += box(110 + i * 580, 290, 540, 660, f'<div style="background:{cols[i]};border-bottom:4px solid {NOCHE};padding:22px 28px" class="big"><span style="font-size:60px">{t}</span></div><div style="padding:10px 28px">' + "".join(
        f'<div style="display:flex;gap:18px;margin-top:28px"><div class="big" style="font-size:60px;width:40px;color:{cols[i] if i else NOCHE}">{k + 1}</div><div style="font-size:27px;font-weight:700;line-height:1.25">{it}</div></div>' for k, it in enumerate(items)) + "</div>")
slide("24_recomendaciones", "menta", "Recomendaciones", "", c)

# =====================================================================================
# 25 · Referencias (APA 7)
refs = [
    "Asamblea Nacional del Ecuador. (2021). <i>Ley Orgánica de Protección de Datos Personales</i>. Registro Oficial Suplemento 459.",
    "El Diario. (2025). Expertos en talento humano priorizan las habilidades blandas en la contratación.",
    "Järvelin, K., &amp; Kekäläinen, J. (2002). Cumulated gain-based evaluation of IR techniques. <i>ACM Transactions on Information Systems, 20</i>(4), 422–446.",
    "Primicias. (2025, 2026). Cifras de desempleo, informalidad y desempleados sin experiencia en Ecuador.",
    "Qwen Team. (2025). <i>Qwen3 technical report</i>. arXiv:2505.09388.",
    "Raghavan, M., Barocas, S., Kleinberg, J., &amp; Levy, K. (2020). Mitigating bias in algorithmic hiring. <i>Proceedings of FAT* 2020</i>, 469–481.",
    "Tabassi, E. (2023). <i>AI Risk Management Framework (AI RMF 1.0)</i>. NIST AI 100-1.",
    "Documentación oficial: LM Studio, FastAPI, React, PyMuPDF, SQLite y Pydantic (consultada en 2026).",
]
c = '<div style="position:absolute;left:110px;top:280px;width:1700px">' + "".join(
    f'<div style="font-size:24px;font-weight:500;line-height:1.4;padding:12px 0 12px 46px;text-indent:-46px;border-bottom:2px solid #E3E1F0">{r}</div>' for r in refs) + "</div>"
slide("25_referencias", "blanco", "Referencias bibliográficas", "", c)

# =====================================================================================
# 26 · Cierre
c = f'<div style="position:absolute;left:110px;top:430px"><div class="big" style="font-size:300px;color:{NOCHE}">¿Preguntas?</div><div style="font-size:40px;font-weight:700;margin-top:20px">Contrate con criterio. La IA ordena; usted decide.</div></div>'
slide("26_cierre", "menta", "HireMind", "", c)

print("ok", len(list(OUT.glob("*.html"))), "diapositivas")
print(f"punto de equilibrio {equilibrio:.1f} · contribución {contrib:.0f} · fijos {fijos} · amort {amort:.0f} · agencia {agencia:.0f}")
