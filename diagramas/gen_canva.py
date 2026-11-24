"""Genera los 3 diagramas del agente de preselección de CVs como SVG 1920x1080."""
import sys
from pathlib import Path
from html import escape

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

BG = "#FFFFFF"
INK = "#0A0147"
MUTED = "#4A4870"
TEAL = "#0A0147"
TEAL2 = "#5383FF"
TEAL_L = "#E6EDFF"
GOLD = "#0FA37A"
GOLD_L = "#D9FBEF"
CORAL = "#E5484D"
CORAL_L = "#FFE4E5"
WHITE = "#FFFFFF"
FONT = "Montserrat, 'Open Sans', sans-serif"


def head():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" font-family="{FONT}">
<defs>
  <filter id="sh" x="-10%" y="-10%" width="120%" height="130%">
    <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0F4C5C" flood-opacity="0.13"/>
  </filter>
  {''.join(f'<marker id="ar-{n}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for n, c in [('t', TEAL), ('g', GOLD), ('c', CORAL), ('m', MUTED)])}
</defs>
<rect width="1920" height="1080" fill="{BG}"/>
"""


def text(x, y, lines, size=18, weight=500, fill=INK, anchor="middle", lh=1.25):
    if isinstance(lines, str):
        lines = lines.split("\n")
    n = len(lines)
    y0 = y - (n - 1) * size * lh / 2
    spans = "".join(
        f'<tspan x="{x}" y="{y0 + i * size * lh:.1f}">{escape(l)}</tspan>' for i, l in enumerate(lines)
    )
    return f'<text font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="central">{spans}</text>'


def title(t, sub):
    return ""
    return (
        f'<rect x="80" y="70" width="10" height="70" rx="5" fill="{GOLD}"/>'
        + text(110, 92, t, 46, 700, TEAL, "start")
        + text(110, 135, sub, 21, 500, MUTED, "start")
    )


def card(x, y, w, h, t, sub=None, accent=TEAL, fill=WHITE, num=None, tsize=19, ssize=15, tcolor=INK):
    """Tarjeta con barra de acento superior; (x,y) es la esquina superior izquierda."""
    s = f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{accent}" stroke-opacity="0.35"/></g>'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="6" rx="3" fill="{accent}"/>'
    tl = t.split("\n")
    sl = sub.split("\n") if sub else []
    th = len(tl) * tsize * 1.22
    sh = len(sl) * ssize * 1.3
    gap = 8 if sl else 0
    top = y + 3 + (h - th - sh - gap) / 2
    s += text(x + w / 2, top + th / 2, tl, tsize, 700, tcolor)
    if sl:
        s += text(x + w / 2, top + th + gap + sh / 2, sl, ssize, 500, MUTED, lh=1.3)
    if num is not None:
        s += f'<circle cx="{x+4}" cy="{y+4}" r="17" fill="{accent}" stroke="{BG}" stroke-width="3"/>'
        s += text(x + 4, y + 5, str(num), 16, 700, WHITE)
    return s


def diamond(cx, cy, w, h, t, accent=TEAL):
    pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
    return (
        f'<g filter="url(#sh)"><polygon points="{pts}" fill="{WHITE}" stroke="{accent}" stroke-width="2.5" stroke-linejoin="round"/></g>'
        + text(cx, cy, t, 17, 700, accent)
    )


def arrow(d, color=TEAL, dashed=False, w=2.6, both=False, mk="t"):
    da = ' stroke-dasharray="9 7"' if dashed else ""
    ms = f' marker-start="url(#ar-{mk})"' if both else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"{da} stroke-linejoin="round" marker-end="url(#ar-{mk})"{ms}/>'


def label(x, y, t, color=TEAL, size=15, bg=BG, weight=600, anchor="middle"):
    lines = t.split("\n")
    wpx = max(len(l) for l in lines) * size * 0.6 + 16
    hpx = len(lines) * size * 1.25 + 8
    bx = x - wpx / 2 if anchor == "middle" else x - 8
    return (
        f'<rect x="{bx:.0f}" y="{y-hpx/2:.0f}" width="{wpx:.0f}" height="{hpx:.0f}" rx="6" fill="{bg}"/>'
        + text(x, y, lines, size, weight, color, anchor)
    )


def pill(x, y, w, h, t, fill, color, size=17, weight=600):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}"/>' + text(x + w / 2, y + h / 2, t, size, weight, color)


def person(cx, cy, color, s=1.0):
    return (
        f'<g transform="translate({cx},{cy}) scale({s})" fill="{color}">'
        f'<circle cx="0" cy="-22" r="18"/><path d="M-32,30 a32,30 0 0 1 64,0 z"/></g>'
    )


def foot(t):
    return text(1840, 1055, t, 13, 500, MUTED, "end")


# ---------------------------------------------------------------- 1. Arquitectura
def arquitectura():
    s = head()
    s += title("Arquitectura del agente", "Preselección de hojas de vida para PYMEs · todo se ejecuta en el equipo local")

    # Reclutador
    s += f'<g filter="url(#sh)"><rect x="50" y="410" width="215" height="300" rx="14" fill="{WHITE}" stroke="{CORAL}" stroke-opacity="0.35"/></g>'
    s += f'<rect x="50" y="410" width="215" height="6" rx="3" fill="{CORAL}"/>'
    s += person(157, 485, CORAL, 1.0)
    s += text(157, 568, "Reclutador\nde la PYME", 21, 700, INK)
    s += text(157, 643, "define criterios,\nsube CVs y toma\nla decisión final", 15, 500, MUTED, lh=1.3)
    # mover texto: el card ya centra; el icono se superpone arriba -> se dibuja card más alto
    # Frontera local
    s += f'<rect x="300" y="190" width="1295" height="850" rx="26" fill="none" stroke="{TEAL}" stroke-width="2.5" stroke-dasharray="12 9"/>'
    s += pill(330, 172, 560, 38, "Equipo local de la PYME  ·  16 GB RAM  ·  los CV no salen", TEAL, WHITE, 16)

    # Interfaz web (React)
    s += f'<g filter="url(#sh)"><rect x="340" y="235" width="1215" height="130" rx="16" fill="{WHITE}" stroke="{TEAL}" stroke-opacity="0.35"/></g>'
    s += f'<path d="M356,235 h204 v130 h-204 a16,16 0 0 1 -16,-16 v-98 a16,16 0 0 1 16,-16 z" fill="{TEAL}"/>'
    s += text(450, 285, "Interfaz web", 18, 500, "#C9C6F2")
    s += text(450, 312, "React", 24, 700, WHITE)
    for i, (t, sub) in enumerate([
        ("Panel y vacantes", "criterios y ponderaciones"),
        ("Cargar hojas de vida", "arrastrar varios PDF"),
        ("Ver ranking", "justificación · evidencias · corregir"),
    ]):
        x = 590 + i * 322
        s += f'<rect x="{x}" y="258" width="300" height="84" rx="12" fill="{TEAL_L}"/>'
        s += text(x + 150, 288, t, 19, 700, TEAL)
        s += text(x + 150, 316, sub, 15, 500, MUTED)

    # Núcleo Python
    s += f'<g filter="url(#sh)"><rect x="340" y="420" width="725" height="590" rx="18" fill="{TEAL_L}" stroke="{TEAL}" stroke-opacity="0.45"/></g>'
    s += text(370, 455, "Núcleo del agente · Python + FastAPI", 24, 700, TEAL, "start")
    mods = [
        ("Ingesta de documentos", "PyMuPDF extrae el texto\nde PDF digitales"),
        ("Cliente LLM", "OpenAI SDK · prompt con\nesquema JSON de salida"),
        ("Validador de salida", "sintaxis, campos y tipos\nreintento si falla"),
        ("Verificador de evidencia", "cada afirmación debe\ntener cita en el CV"),
        ("Filtro de equidad", "ignora foto, género, edad,\nnacionalidad, religión"),
        ("Motor de puntuación", "reglas + ponderaciones\nPuntaje = Σ wᵢ · sᵢ"),
    ]
    for i, (t, sub) in enumerate(mods):
        col, row = i % 2, i // 2
        acc = GOLD if i == 5 else TEAL2
        s += card(370 + col * 345, 490 + row * 172, 320, 145, t, sub, accent=acc, num=i + 1, tsize=19, ssize=15)

    # LM Studio
    s += f'<g filter="url(#sh)"><rect x="1170" y="420" width="385" height="300" rx="18" fill="{GOLD_L}" stroke="{GOLD}" stroke-opacity="0.6"/></g>'
    s += text(1362, 458, "LM Studio", 25, 700, "#065F46")
    s += text(1362, 488, "servidor local compatible con OpenAI", 15, 500, MUTED)
    s += pill(1235, 506, 255, 32, "localhost:1234/v1", WHITE, "#065F46", 16, 600)
    s += f'<rect x="1195" y="556" width="335" height="74" rx="12" fill="{GOLD}"/>'
    s += text(1362, 582, "Qwen3-4B-Instruct-2507", 20, 700, WHITE)
    s += text(1362, 608, "GGUF Q4_K_M · ≈2,5 GB · contexto 8k", 14, 500, "#E8FFF6")
    s += text(1362, 662, "Solo extrae datos y redacta", 16, 700, "#065F46")
    s += text(1362, 686, "la justificación: no pone la nota", 16, 500, "#065F46")

    # SQLite
    s += f'<g filter="url(#sh)"><rect x="1170" y="765" width="385" height="245" rx="18" fill="{WHITE}" stroke="{TEAL}" stroke-opacity="0.35"/></g>'
    s += f'<g transform="translate(1210,800)" fill="none" stroke="{TEAL}" stroke-width="3"><ellipse cx="18" cy="0" rx="18" ry="7"/><path d="M0,0 v28 a18,7 0 0 0 36,0 v-28"/><path d="M0,14 a18,7 0 0 0 36,0"/></g>'
    s += text(1262, 806, "SQLite", 25, 700, TEAL, "start")
    s += text(1262, 834, "base de datos local, sin servidor", 15, 500, MUTED, "start")
    for i, t in enumerate(["vacantes", "candidatos", "evaluaciones", "evidencias"]):
        x = 1195 + (i % 2) * 172
        y = 870 + (i // 2) * 58
        s += pill(x, y, 160, 44, t, TEAL_L, TEAL, 16)

    # Escalamiento opcional
    s += f'<rect x="1625" y="420" width="260" height="300" rx="18" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="8 7"/>'
    s += text(1755, 452, "Escalamiento opcional", 17, 700, MUTED)
    s += card(1645, 478, 220, 108, "Qwen3-8B\nMistral-7B", "más razonamiento", accent=MUTED, tsize=17, ssize=14)
    s += card(1645, 600, 220, 108, "Gemini Flash\n(nube)", "volumen masivo", accent=MUTED, tsize=17, ssize=14)

    # Flechas
    s += arrow("M265,520 H312 V300 H340", CORAL, both=True, mk="c")
    s += arrow("M560,365 V420", TEAL, both=True)
    s += label(800, 393, "API REST · FastAPI · localhost:8000   (vacante y CVs ↓  resultados ↑)", TEAL, 14)
    s += arrow("M1065,545 H1170", GOLD, mk="g")
    s += label(1117, 525, "prompt", GOLD, 14, TEAL_L if False else BG)
    s += arrow("M1170,600 H1065", GOLD, mk="g")
    s += label(1117, 620, "JSON", GOLD, 14)
    s += arrow("M1065,890 H1170", TEAL, both=True)
    s += label(1117, 870, "guarda", TEAL, 14)
    s += label(1117, 910, "lee", TEAL, 14)
    s += arrow("M1555,570 H1625", MUTED, dashed=True, mk="m")
    s += foot("Herramientas: React · Vite · Tailwind · FastAPI · Python · PyMuPDF · LM Studio · Qwen3-4B · OpenAI SDK · SQLite")
    return s + "</svg>"


# ---------------------------------------------------------------- 2. Razonamiento
def razonamiento():
    s = head()
    s += title("Flujo de razonamiento del agente", "Lo que el agente hace con cada hoja de vida, paso a paso")
    s += pill(1110, 190, 250, 40, "El LLM extrae y redacta", GOLD_L, "#065F46", 16)
    s += pill(1372, 190, 300, 40, "Python valida, verifica y puntúa", TEAL_L, TEAL, 16)
    s += pill(1684, 190, 196, 40, "La persona decide", CORAL_L, CORAL, 16)

    # carriles
    lanes = [
        (255, 215, GOLD_L, GOLD, "LLM · Qwen 4B"),
        (480, 330, TEAL_L, TEAL, "Python · reglas"),
        (820, 225, CORAL_L, CORAL, "Controles y humano"),
    ]
    for y, h, fill, col, name in lanes:
        s += f'<rect x="250" y="{y}" width="1640" height="{h}" rx="16" fill="{fill}" fill-opacity="0.65"/>'
        s += f'<rect x="250" y="{y}" width="46" height="{h}" rx="12" fill="{col}"/>'
        s += f'<text transform="translate(273,{y+h/2}) rotate(-90)" font-size="16" font-weight="700" fill="{WHITE}" text-anchor="middle" dominant-baseline="central">{escape(name)}</text>'

    C = [400 + 178 * i for i in range(8)]
    W, H = 160, 150
    LY, PY = 365, 645  # centros de carril

    # entradas
    s += card(45, 290, 175, 150, "Vacante", "criterios y\nponderaciones", accent=TEAL2, tsize=20)
    s += card(45, 570, 175, 150, "Hoja de vida", "PDF del\ncandidato", accent=TEAL2, tsize=20)

    def c(i, y, t, sub, acc=TEAL, num=None, **kw):
        return card(C[i] - W / 2, y - H / 2, W, H, t, sub, accent=acc, num=num, tsize=18, ssize=14, **kw)

    s += c(0, PY, "Leer\ndocumento", "PyMuPDF", num=1)
    s += diamond(C[1], PY, 168, 150, "¿Texto\nlegible?")
    s += c(2, LY, "Extraer a\nJSON", "formación, exp.,\nhabilidades, proyectos\n+ cita textual", acc=GOLD, num=2)
    s += diamond(C[3], PY, 168, 150, "¿JSON\nválido?")
    s += c(4, PY, "Verificar\nevidencia", "¿la cita existe\nen el CV?", num=4)
    s += c(5, PY, "Excluir datos\npersonales", "no se usan\npara puntuar", num=5)
    s += c(6, PY, "Comparar y\npuntuar", "Σ wᵢ · sᵢ\ncumple · parcial ·\nno identificado", num=6, acc=TEAL)
    s += c(7, LY, "Redactar\njustificación", "solo con las\nevidencias\nverificadas", acc=GOLD, num=7)
    s += c(7, PY, "Resultado", "puntaje +\nevidencias\n→ SQLite", num=8, acc=TEAL2)
    # pasos numerados en rombos
    for i, n in ((1, None), (3, 3)):
        if n:
            s += f'<circle cx="{C[i]-50}" cy="{PY-55}" r="17" fill="{TEAL}" stroke="{BG}" stroke-width="3"/>' + text(C[i] - 50, PY - 54, str(n), 16, 700, WHITE)

    # controles
    s += card(330, 885, 300, 120, "Revisión manual", "PDF escaneado, ilegible o\nJSON que falla 2 veces", accent=CORAL, tsize=19)
    s += card(C[4] - 82, 885, 164, 120, "«No verificado»", "sin cita → 0 pts\n(no se inventa)", accent=CORAL, tsize=16, ssize=14)
    s += card(C[5] - 82, 885, 164, 120, "Ignorados", "foto, género, edad,\nnacionalidad,\nreligión", accent=CORAL, tsize=16, ssize=13)
    s += card(1585, 870, 290, 150, "Decide la persona", "revisa los CV del top 5,\ncorrige errores y elige\na quién entrevistar", accent=CORAL, tsize=20, ssize=15)

    # flechas principales
    s += arrow(f"M220,{PY} H{C[0]-W/2}")
    s += arrow(f"M{C[0]+W/2},{PY} H{C[1]-84}")
    s += arrow(f"M{C[1]+84},{PY} H{C[2]-30} V{LY+H/2}")
    s += label(C[1] + 110, PY - 18, "sí", TEAL, 15, TEAL_L)
    s += arrow(f"M{C[2]+W/2},{LY} H{C[3]} V{PY-75}", GOLD, mk="g")
    s += label(C[3] - 10, LY - 22, "JSON + citas", GOLD, 14, GOLD_L)
    s += arrow(f"M{C[3]+84},{PY} H{C[4]-W/2}")
    s += label(C[3] + 98, PY - 18, "sí", TEAL, 15, TEAL_L)
    s += arrow(f"M{C[4]+W/2},{PY} H{C[5]-W/2}")
    s += arrow(f"M{C[5]+W/2},{PY} H{C[6]-W/2}")
    s += arrow(f"M{C[6]+45},{PY-H/2} V{LY} H{C[7]-W/2}")
    s += arrow(f"M{C[7]},{LY+H/2} V{PY-H/2}", GOLD, mk="g")
    s += arrow(f"M{C[7]+40},{PY+H/2} V870")
    # vacante -> comparar
    s += arrow(f"M132,290 V272 H{C[6]} V{PY-H/2}", TEAL2, dashed=True)
    s += label(1040, 272, "criterios y pesos wᵢ de la vacante", TEAL2, 14, GOLD_L)

    # ramas de control
    s += arrow(f"M{C[1]},{PY+75} V885", CORAL, mk="c")
    s += label(C[1] + 22, 790, "no", CORAL, 15, TEAL_L)
    s += arrow(f"M{C[3]},{PY+75} V860 H{C[2]+30} V{LY+H/2}", CORAL, dashed=True, mk="c")
    s += label(C[3] + 22, 760, "no", CORAL, 15, TEAL_L)
    s += label(C[2] + 95, 843, "reintenta con el error (máx. 2)", CORAL, 14, CORAL_L)
    s += arrow(f"M{C[3]},860 V945 H630", CORAL, dashed=True, mk="c")
    s += arrow(f"M{C[4]},{PY+H/2} V885", CORAL, dashed=True, mk="c")
    s += arrow(f"M{C[5]},{PY+H/2} V885", CORAL, dashed=True, mk="c")
    s += foot("El LLM no asigna la nota final: sᵢ y el puntaje los calcula Python con las ponderaciones del reclutador.")
    return s + "</svg>"


# ---------------------------------------------------------------- 3. Flujo de trabajo
def trabajo():
    s = head()
    s += title("Flujo de trabajo", "De la vacante al ranking: quién hace qué en cada paso")
    lanes = [
        ("Reclutador", CORAL, CORAL_L),
        ("React\n(interfaz)", TEAL, WHITE),
        ("Python\n(agente)", TEAL, TEAL_L),
        ("LM Studio\nQwen 4B", GOLD, GOLD_L),
        ("SQLite", TEAL2, WHITE),
    ]
    Y0, LH = 185, 165
    for i, (n, col, fill) in enumerate(lanes):
        y = Y0 + i * LH
        s += f'<rect x="60" y="{y+4}" width="1830" height="{LH-8}" rx="14" fill="{fill}" fill-opacity="0.75"/>'
        s += f'<rect x="60" y="{y+4}" width="170" height="{LH-8}" rx="14" fill="{col}"/>'
        s += text(145, y + LH / 2, n, 19, 700, WHITE)
    cy = [Y0 + LH * i + LH / 2 for i in range(5)]
    C = [345 + 197 * i for i in range(8)]
    W, H = 172, 112

    def c(col, lane, t, sub, num, acc=None, **kw):
        acc = acc or [CORAL, TEAL, TEAL, GOLD, TEAL2][lane]
        return card(C[col] - W / 2, cy[lane] - H / 2, W, H, t, sub, accent=acc, num=num, tsize=16, ssize=13, **kw)

    def v(col, a, b, color=TEAL, mk="t", dx=0, **kw):  # flecha vertical entre carriles
        y1 = cy[a] + (H / 2 if b > a else -H / 2)
        y2 = cy[b] + (-H / 2 if b > a else H / 2)
        return arrow(f"M{C[col]+dx},{y1} V{y2}", color, mk=mk, **kw)

    # bucle por CV (fondo)
    s += f'<rect x="{C[2]-100}" y="{cy[2]-72}" width="{C[5]-C[2]+200}" height="{cy[3]-cy[2]+144}" rx="18" fill="none" stroke="{TEAL}" stroke-width="2" stroke-dasharray="6 6"/>'
    s += pill(C[4] - 140, cy[2] - 89, 290, 34, "↻ se repite para cada CV", TEAL, WHITE, 15)

    s += c(0, 0, "Inicia LM Studio", "carga Qwen3-4B", 1)
    s += c(0, 3, "Servidor API", "localhost:1234/v1\nlisto", 2)
    s += v(0, 0, 3, GOLD, "g", dashed=True)

    s += c(1, 0, "Registra la vacante", "criterios y\nponderaciones", 3)
    s += c(1, 1, "Formulario", "de vacante", 4)
    s += c(1, 2, "Valida pesos", "suman 100 %", 5)
    s += c(1, 4, "Guarda vacante", "tabla vacantes", 6)
    s += v(1, 0, 1) + v(1, 1, 2) + v(1, 2, 4)

    s += c(2, 0, "Sube las hojas\nde vida", "varios PDF", 7)
    s += c(2, 1, "Carga de archivos", "subida múltiple", 8)
    s += c(2, 2, "Extrae texto", "PyMuPDF", 9)
    s += v(2, 0, 1) + v(2, 1, 2)

    s += c(3, 2, "Arma el prompt", "texto + esquema\nJSON", 10)
    s += arrow(f"M{C[2]+W/2},{cy[2]} H{C[3]-W/2}")
    s += c(3, 3, "Extrae datos", "formación, exp.,\nhabilidades, proyectos", 11)
    s += v(3, 2, 3, GOLD, "g")
    s += c(4, 2, "Valida y verifica", "JSON válido +\ncitas en el CV", 12)
    s += arrow(f"M{C[3]+W/2},{cy[3]} H{C[4]} V{cy[2]+H/2}", GOLD, mk="g")
    s += label(C[3] + W / 2 + 50, cy[3] - 14, "JSON", GOLD, 14, GOLD_L)

    s += c(5, 2, "Calcula puntaje", "Σ wᵢ · sᵢ", 13, acc=GOLD)
    s += arrow(f"M{C[4]+W/2},{cy[2]} H{C[5]-W/2}")
    s += c(5, 4, "Guarda resultado", "candidato, puntaje\ny evidencias", 14)
    s += v(5, 2, 4, dx=0)

    s += c(6, 1, "Ranking", "ordena todos los CV\ncon justificación\ny evidencias", 15)
    s += arrow(f"M{C[5]+W/2},{cy[4]} H{C[6]} V{cy[1]+H/2}")
    s += label(C[6], cy[3] + 30, "consulta", TEAL, 14, GOLD_L)

    s += c(7, 0, "Revisa el top 5", "y decide a quién\nentrevistar", 16, acc=CORAL)
    s += arrow(f"M{C[6]+W/2},{cy[1]} H{C[7]} V{cy[0]+H/2}")
    s += arrow(f"M{C[7]+W/2},{cy[0]} H1860 V{cy[2]} H{C[5]+W/2}", CORAL, dashed=True, mk="c")
    s += label(1720, cy[2] - 22, "corrige un dato → recalcula", CORAL, 14, TEAL_L)
    s += pill(C[7] - W/2 - 215, cy[0] - 17, 190, 34, "decisión humana", CORAL, WHITE, 15)
    s += foot("Objetivo: < 15 s por CV · Medido con Qwen3-4B Q4_K_M en GPU de 8 GB: 9,4 s promedio · P95 11,4 s (14 CV)")
    return s + "</svg>"



import re
SLIDES = [
    ("A_arquitectura", arquitectura, "#2EE5A7", "#0A0147", "Arquitectura completa del agente", "#0A0147"),
    ("B_razonamiento", razonamiento, "#0A0147", "#FFFFFF", "Flujo de razonamiento del agente", "#FD696E"),
]
for name, fn, bg, tc, t, deco in SLIDES:
    inner = fn()
    inner = re.sub(r"<svg [^>]*>", '<svg x="52" y="182" width="1816" height="864" viewBox="30 160 1870 905" font-family="%s">' % FONT, inner, count=1)
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">'
           f'<rect width="1920" height="1080" fill="{bg}"/>'
           f'<rect x="1560" y="1056" width="300" height="24" fill="{deco}"/><rect x="60" y="0" width="240" height="22" fill="{deco}"/>'
           f'<text x="960" y="118" font-family="Bebas Neue" font-size="100" fill="{tc}" text-anchor="middle" letter-spacing="1">{escape(t.upper())}</text>'
           f'<rect x="40" y="170" width="1840" height="886" rx="26" fill="#FFFFFF"/>'
           + inner + '</svg>')
    (OUT / f"{name}.svg").write_text(out, encoding="utf-8")
    print(name)
