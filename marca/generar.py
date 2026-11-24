"""Genera 3 manuales de marca de HireMind (HTML -> PDF con Chrome).

    python3 generar.py            # escribe html/ y los PDF en esta carpeta
"""
from __future__ import annotations

import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
HTML = AQUI / "html"
FECHA = "Noviembre 2026"

# ------------------------------------------------------------------ utilidades de color
def _lin(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(hexa: str) -> float:
    h = hexa.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contraste(a: str, b: str) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def rgb(hexa: str) -> str:
    h = hexa.lstrip("#")
    return " · ".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def nivel(r: float, grande=False) -> str:
    if r >= 7:
        return "AAA"
    if r >= 4.5:
        return "AA"
    if r >= 3:
        return "AA texto grande" if not grande else "AA"
    return "No apto"


# ------------------------------------------------------------------ marcas
MARCAS = {
    "A": dict(
        archivo="Manual_Marca_HireMind_A_Energia",
        nombre="Energía", subtitulo="Pop geométrico · basada en la presentación de Canva",
        idea="Contratar es una decisión importante, pero no tiene por qué sentirse pesada. "
             "HireMind se presenta como un aliado cercano y con energía: colores planos, bloques "
             "geométricos y titulares grandes que se leen de lejos, igual que en nuestra presentación.",
        tagline="Contrata con criterio, no a ciegas.",
        adjetivos=[("Cercana", "Habla como un colega de la PYME, no como un software."),
                   ("Enérgica", "Titulares cortos, verbos activos, colores vivos."),
                   ("Clara", "Una idea por bloque. Nada de letra chiquita."),
                   ("Honesta", "Dice qué no pudo verificar en el CV.")],
        decimos=["“Revisa el top 5 y decide tú.”", "“Este dato no aparece en el CV.”", "“Listo: 14 hojas de vida ordenadas.”"],
        nodecimos=["“Nuestra IA elige al mejor candidato.”", "“Algoritmo avanzado de última generación.”", "“Candidato descartado.”"],
        colores=[("Azul noche", "#0A0147", "Texto, logo, bloques de contraste", 30),
                 ("Menta", "#2EE5A7", "Fondo de marca, éxito, “cumple”", 30),
                 ("Coral", "#FD696E", "Titulares, acción principal, acentos", 20),
                 ("Azul eléctrico", "#5383FF", "Información, enlaces, gráficos", 10),
                 ("Blanco", "#FFFFFF", "Superficies y respiración", 10)],
        apoyo=[("Menta claro", "#D9FBEF"), ("Coral claro", "#FFE4E5"), ("Azul claro", "#E6EDFF"), ("Ámbar parcial", "#FFB547")],
        pares=[("#0A0147", "#FFFFFF"), ("#0A0147", "#2EE5A7"), ("#FFFFFF", "#0A0147"), ("#0A0147", "#FD696E"), ("#FFFFFF", "#5383FF"), ("#FD696E", "#FFFFFF")],
        fuente_d="Bebas Neue", fuente_t="Montserrat", fuente_n="Montserrat",
        gfonts="family=Bebas+Neue&family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;0,800;1,700",
        desc_d="Condensada, mayúsculas, impacto de cartel. Solo para titulares y cifras grandes.",
        desc_t="Geométrica y amable. Texto, botones y datos. Itálica negrita para etiquetas.",
        principios=[("Rebote", "Los elementos llegan con un pequeño rebote, como bloques que encajan."),
                    ("Deslizamiento", "Los bloques entran desde los bordes, nunca aparecen de la nada."),
                    ("Contacto", "Al presionar, el botón se hunde en su sombra dura.")],
        easings=[("Entrada con rebote", "cubic-bezier(.34,1.56,.64,1)", .34, 1.56, .64, 1, "360 ms"),
                 ("Salida rápida", "cubic-bezier(.55,0,1,.45)", .55, 0, 1, .45, "180 ms"),
                 ("Presión", "steps / lineal", 0, 0, 1, 1, "90 ms")],
    ),
    "B": dict(
        archivo="Manual_Marca_HireMind_B_Criterio",
        nombre="Criterio", subtitulo="Editorial · sobria y confiable",
        idea="La diferencia de HireMind es la evidencia: cada dato viene con su cita del CV. "
             "Esta propuesta lo convierte en identidad. Una tipografía con serifa de revista, "
             "colores de tierra andina y la comilla como símbolo transmiten seriedad y cuidado con las personas.",
        tagline="Cada decisión, con su evidencia.",
        adjetivos=[("Serena", "Ritmo pausado, mucho espacio en blanco."),
                   ("Confiable", "Todo lo que afirma lo puede mostrar."),
                   ("Humana", "Las personas deciden; la herramienta acompaña."),
                   ("Precisa", "Palabras exactas, sin exageraciones.")],
        decimos=["“Según el CV: «Excel avanzado (tablas dinámicas)».”", "“No se encontró evidencia para este criterio.”", "“La decisión final es suya.”"],
        nodecimos=["“¡Encuentra al candidato perfecto en segundos!”", "“La IA sabe quién es mejor.”", "“Rechazado.”"],
        colores=[("Bosque", "#123B32", "Logo, titulares, acción principal", 30),
                 ("Arena", "#F3EDE2", "Fondo de marca y documentos", 35),
                 ("Terracota", "#C65D3B", "Acentos, citas, énfasis", 15),
                 ("Ocre", "#D9A441", "Resaltador de evidencias, parcial", 10),
                 ("Tinta", "#1B1B18", "Texto de lectura", 10)],
        apoyo=[("Salvia", "#DCE6DF"), ("Arena oscura", "#E4D9C6"), ("Terracota claro", "#F3DDD3"), ("Verde éxito", "#2F7D5B")],
        pares=[("#1B1B18", "#F3EDE2"), ("#F3EDE2", "#123B32"), ("#123B32", "#F3EDE2"), ("#FFFFFF", "#C65D3B"), ("#1B1B18", "#D9A441"), ("#123B32", "#DCE6DF")],
        fuente_d="Fraunces", fuente_t="Inter", fuente_n="Inter",
        gfonts="family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,600&family=Inter:wght@400;500;600;700",
        desc_d="Serifa editorial con carácter. Titulares, citas y cifras. La itálica marca la palabra “mind”.",
        desc_t="Neutra y muy legible en pantalla. Interfaz, tablas y textos largos.",
        principios=[("Calma", "Fundidos suaves y cortos; nada salta ni rebota."),
                    ("Evidencia", "El resaltador recorre la cita: la animación muestra de dónde sale el dato."),
                    ("Continuidad", "Lo que cambia se desplaza con suavidad; no se reemplaza de golpe.")],
        easings=[("Suave", "cubic-bezier(.22,1,.36,1)", .22, 1, .36, 1, "280 ms"),
                 ("Resaltador", "cubic-bezier(.65,0,.35,1)", .65, 0, .35, 1, "600 ms"),
                 ("Salida", "cubic-bezier(.4,0,1,1)", .4, 0, 1, 1, "160 ms")],
    ),
    "C": dict(
        archivo="Manual_Marca_HireMind_C_Senal",
        nombre="Señal", subtitulo="Tecnológica · precisa y moderna",
        idea="Entre cientos de hojas de vida, HireMind encuentra la señal. Esta propuesta muestra el "
             "lado tecnológico del producto: modo oscuro, luz violeta y cian, números en tipografía "
             "monoespaciada y un símbolo hecho de barras de ranking con una persona en la cima: quien decide.",
        tagline="Señal clara entre cientos de CV.",
        adjetivos=[("Precisa", "Datos exactos: 9,4 s, 100 %, 5 de 7."),
                   ("Moderna", "Interfaz oscura, luz y profundidad."),
                   ("Transparente", "Muestra el proceso, no solo el resultado."),
                   ("Ágil", "Respuestas rápidas, textos breves.")],
        decimos=["“14 CV procesados · 9,4 s promedio.”", "“Cita verificada en el documento.”", "“Top 5 listo para su revisión.”"],
        nodecimos=["“Magia de inteligencia artificial.”", "“Confíe en el algoritmo.”", "“Puntaje final definitivo.”"],
        colores=[("Noche", "#0B0D17", "Fondo principal de la interfaz", 40),
                 ("Violeta", "#7C5CFF", "Marca, acción principal", 20),
                 ("Cian", "#22D3EE", "Señal, foco, datos en vivo", 15),
                 ("Lima", "#B8F35A", "Cumple, éxito, modelo activo", 10),
                 ("Niebla", "#E7E9F5", "Texto sobre oscuro", 15)],
        apoyo=[("Grafito", "#161A2B"), ("Pizarra", "#262B42"), ("Gris texto", "#9AA0BC"), ("Ámbar parcial", "#FFC14D")],
        pares=[("#E7E9F5", "#0B0D17"), ("#FFFFFF", "#7C5CFF"), ("#0B0D17", "#22D3EE"), ("#0B0D17", "#B8F35A"), ("#9AA0BC", "#0B0D17"), ("#E7E9F5", "#161A2B")],
        fuente_d="Space Grotesk", fuente_t="Space Grotesk", fuente_n="JetBrains Mono",
        gfonts="family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600",
        desc_d="Grotesca geométrica con rasgos técnicos. Titulares e interfaz.",
        desc_t="Monoespaciada para cifras, puntajes y tiempos: los números se alinean y se leen como datos.",
        principios=[("Escaneo", "Una línea de luz recorre el CV mientras se procesa."),
                    ("Conteo", "Las cifras suben hasta su valor; el puntaje se “calcula” frente al usuario."),
                    ("Pulso", "El estado en vivo late con un brillo sutil, nunca parpadea.")],
        easings=[("Estándar", "cubic-bezier(.2,.8,.2,1)", .2, .8, .2, 1, "240 ms"),
                 ("Conteo", "cubic-bezier(.16,1,.3,1)", .16, 1, .3, 1, "900 ms"),
                 ("Escaneo", "lineal", 0, 0, 1, 1, "1 400 ms")],
    ),
}

# ------------------------------------------------------------------ logos (SVG)
def simbolo(m: str, tam=64, mono: str | None = None, fondo=True) -> str:
    """Símbolo de cada marca. mono = un solo color para versiones monocromas."""
    if m == "A":
        nv, co, mi = mono or "#0A0147", mono or "#FD696E", "#2EE5A7"
        base = f'<rect x="10" y="10" width="50" height="50" fill="{mi}"/>' if fondo and not mono else ""
        return (f'<svg viewBox="0 0 64 64" width="{tam}" height="{tam}" aria-label="Símbolo HireMind">{base}'
                f'<circle cx="27" cy="27" r="16" fill="#FFFFFF" stroke="{nv}" stroke-width="7"/>'
                f'<path d="M39 39 L55 55" stroke="{nv}" stroke-width="9" stroke-linecap="square"/>'
                f'<path d="M19 27.5 l6 6 l10.5 -12" fill="none" stroke="{co}" stroke-width="5.5" stroke-linecap="square" stroke-linejoin="miter"/></svg>')
    if m == "B":
        bg, fg = (mono, "#FFFFFF") if mono else ("#123B32", "#F3EDE2")
        if mono and not fondo:
            bg, fg = "none", mono
        coma = lambda dx: (f'<circle cx="{22+dx}" cy="38" r="7.5" fill="{fg}"/>'
                           f'<path d="M{14.6+dx} 38.5 C{14.2+dx} 28 {18+dx} 21 {27+dx} 17.5 L{28.6+dx} 21 C{22.5+dx} 24 {20.6+dx} 29 {21+dx} 33 Z" fill="{fg}"/>')
        acento = "" if mono else '<rect x="16" y="49" width="32" height="3.2" rx="1.6" fill="#D9A441"/>'
        return (f'<svg viewBox="0 0 64 64" width="{tam}" height="{tam}" aria-label="Símbolo HireMind">'
                f'<rect width="64" height="64" rx="16" fill="{bg}"/>{coma(0)}{coma(19)}{acento}</svg>')
    # C
    gid = f"g{tam}{mono or ''}".replace("#", "")
    relleno = mono or f"url(#{gid})"
    dot = mono or "#22D3EE"
    defs = "" if mono else (f'<defs><linearGradient id="{gid}" x1="0" y1="1" x2="1" y2="0">'
                            f'<stop offset="0" stop-color="#7C5CFF"/><stop offset="1" stop-color="#22D3EE"/></linearGradient></defs>')
    return (f'<svg viewBox="0 0 64 64" width="{tam}" height="{tam}" aria-label="Símbolo HireMind">{defs}'
            f'<rect x="8" y="36" width="12" height="20" rx="6" fill="{relleno}" opacity=".55"/>'
            f'<rect x="26" y="26" width="12" height="30" rx="6" fill="{relleno}" opacity=".8"/>'
            f'<rect x="44" y="20" width="12" height="36" rx="6" fill="{relleno}"/>'
            f'<circle cx="50" cy="9.5" r="6" fill="{dot}"/></svg>')


def logotipo(m: str, tam=40, color: str | None = None, negativo=False) -> str:
    if m == "A":
        c1, c2 = (color, color) if color else (("#FFFFFF", "#2EE5A7") if negativo else ("#0A0147", "#FD696E"))
        return f'<span class="lt-a" style="font-size:{tam}px"><span style="color:{c1}">HIRE</span><span style="color:{c2}">MIND</span></span>'
    if m == "B":
        c1, c2 = (color, color) if color else (("#F3EDE2", "#D9A441") if negativo else ("#123B32", "#C65D3B"))
        return f'<span class="lt-b" style="font-size:{tam}px"><span style="color:{c1}">Hire</span><em style="color:{c2}">mind</em></span>'
    c1, c2 = (color, color) if color else (("#E7E9F5", "#22D3EE") if negativo else ("#0B0D17", "#7C5CFF"))
    return f'<span class="lt-c" style="font-size:{tam}px;color:{c1}">hire<span style="color:{c2}">mind</span></span>'


def logo(m: str, tam=48, negativo=False, color: str | None = None, apilado=False) -> str:
    s = simbolo(m, tam, mono=color)
    t = logotipo(m, tam * (0.9 if m == "A" else 0.62 if m == "B" else 0.6), color=color, negativo=negativo)
    d = "column" if apilado else "row"
    return f'<span class="logo" style="flex-direction:{d};gap:{tam*0.28:.0f}px">{s}{t}</span>'


# ------------------------------------------------------------------ CSS
CSS_BASE = """
@page { size: 297mm 210mm; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: var(--ft); color: var(--ink); background: #888; }
.page { width: 297mm; height: 210mm; position: relative; overflow: hidden; padding: 15mm 17mm 14mm;
        background: var(--paper); page-break-after: always; break-after: page; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; }
.cab { display: flex; align-items: baseline; gap: 14px; margin-bottom: 9mm; }
.cab .num { font-family: var(--fn); font-size: 12px; color: var(--muted); letter-spacing: .08em; }
.cab h2 { font-family: var(--fd); font-size: var(--h2); line-height: 1; color: var(--title); font-weight: var(--wd); letter-spacing: var(--ls); }
.pie { position: absolute; left: 17mm; right: 17mm; bottom: 7mm; display: flex; justify-content: space-between;
       font-size: 9px; color: var(--muted); letter-spacing: .04em; }
.logo { display: inline-flex; align-items: center; }
.lt-a { font-family: 'Bebas Neue'; letter-spacing: .02em; line-height: .9; }
.lt-b { font-family: 'Fraunces'; font-weight: 600; letter-spacing: -.02em; line-height: 1; font-variation-settings: "opsz" 144; }
.lt-b em { font-style: italic; font-weight: 400; }
.lt-c { font-family: 'Space Grotesk'; font-weight: 600; letter-spacing: -.035em; line-height: 1; }
.cols { display: grid; gap: 8mm; flex: 1; min-height: 0; }
.eti { font-size: 9.5px; text-transform: uppercase; letter-spacing: .14em; color: var(--muted); font-weight: 600; margin-bottom: 3mm; }
p { font-size: 12.5px; line-height: 1.55; }
.small { font-size: 10.5px; line-height: 1.45; color: var(--muted); }
.card { background: var(--surface); border-radius: var(--r); padding: 6mm; border: var(--border); }
.mono { font-family: var(--fn); }
table { border-collapse: collapse; width: 100%; font-size: 11px; }
td, th { text-align: left; padding: 2.2mm 2mm; border-bottom: 1px solid var(--line); vertical-align: middle; }
th { font-size: 9px; text-transform: uppercase; letter-spacing: .1em; color: var(--muted); font-weight: 600; }
.ok { color: var(--okt); font-weight: 700; } .no { color: #D2283A; font-weight: 700; }
.frames { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3mm; }
.frame { border-radius: calc(var(--r) * .6); background: var(--surface); border: var(--border); height: 31mm; position: relative;
         display: flex; align-items: center; justify-content: center; overflow: hidden; }
.frame-t { font-family: var(--fn); font-size: 9px; color: var(--muted); margin-top: 1.5mm; text-align: center; }
.sb-tit { display: flex; justify-content: space-between; align-items: baseline; margin: 0 0 2.5mm; }
.sb-tit b { font-size: 12.5px; }
.sb-tit span { font-family: var(--fn); font-size: 9.5px; color: var(--muted); }
.x { position: relative; }
.x::after { content: "✕"; position: absolute; top: 2mm; right: 2.5mm; width: 18px; height: 18px; border-radius: 50%;
            background: #D2283A; color: #fff; font-size: 11px; display: flex; align-items: center; justify-content: center; font-weight: 700; }
"""

CSS_MARCA = {
    "A": """
:root { --paper:#FFFFFF; --ink:#0A0147; --title:#0A0147; --muted:#4A4870; --surface:#FFFFFF; --line:#E3E6F5;
  --fd:'Bebas Neue'; --ft:'Montserrat'; --fn:'Montserrat'; --h2:52px; --wd:400; --ls:.01em; --r:0px; --border:2.5px solid #0A0147; --okt:#0A7F5A;
  --prim:#FD696E; --sec:#0A0147; --acc:#2EE5A7; }
.cab h2 { color:#0A0147 }
.page.deco::before { content:""; position:absolute; top:0; right:24mm; width:62mm; height:7mm; background:#5383FF; }
.page.deco::after { content:""; position:absolute; bottom:0; left:0; width:40mm; height:9mm; background:#0A0147; }
.pie { left:48mm; }
.eti { font-style: italic; font-weight: 800; color: #0A0147; letter-spacing: .06em; font-size: 11px; }
.btn { font-family:'Montserrat'; font-weight:800; font-size:13px; letter-spacing:.04em; text-transform:uppercase; padding:11px 20px;
  border:2.5px solid #0A0147; background:#FD696E; color:#0A0147; box-shadow:4px 4px 0 #0A0147; display:inline-flex; gap:8px; align-items:center; }
.btn.sec { background:#FFFFFF; } .btn.fan { background:transparent; border-color:transparent; box-shadow:none; text-decoration:underline 2.5px; text-underline-offset:5px; }
.btn.peligro { background:#0A0147; color:#FFFFFF; }
.btn.hover { background:#FF858A; transform:translate(-1px,-1px); box-shadow:5px 5px 0 #0A0147; }
.btn.sec.hover { background:#D9FBEF; }
.btn.fan.hover, .btn.fan.press { background:transparent; box-shadow:none; transform:none; color:#FD696E; }
.btn.peligro.hover { background:#1E1470; }
.btn.fan.dis { background:transparent; box-shadow:none; border-color:transparent; }
.btn.press { transform:translate(4px,4px); box-shadow:0 0 0 #0A0147; }
.btn.dis { background:#E6E6EE; color:#9A98B5; border-color:#C9C8DA; box-shadow:4px 4px 0 #C9C8DA; }
.btn.foco { outline:3px solid #5383FF; outline-offset:4px; }
.chip { font-family:'Montserrat'; font-weight:800; font-size:10px; letter-spacing:.06em; text-transform:uppercase; padding:4px 9px; border:2px solid #0A0147; display:inline-block; }
.chip.cu { background:#2EE5A7; } .chip.pa { background:#FFB547; } .chip.ni { background:#FFFFFF; color:#4A4870; border-style:dashed; }
.campo { border:2.5px solid #0A0147; padding:10px 12px; font-size:12px; background:#fff; }
.campo.foco { box-shadow:4px 4px 0 #5383FF; }
.bar { height:12px; background:#E6EDFF; border:2px solid #0A0147; } .bar i { display:block; height:100%; background:#2EE5A7; border-right:2px solid #0A0147; }
""",
    "B": """
:root { --paper:#F3EDE2; --ink:#1B1B18; --title:#123B32; --muted:#6A675E; --surface:#FBF8F2; --line:#E1D8C8;
  --fd:'Fraunces'; --ft:'Inter'; --fn:'Inter'; --h2:40px; --wd:600; --ls:-.02em; --r:14px; --border:1px solid #E1D8C8; --okt:#2F7D5B;
  --prim:#123B32; --sec:#C65D3B; --acc:#D9A441; }
.cab h2 { font-variation-settings:"opsz" 144; }
.cab h2 em { font-style:italic; font-weight:400; color:#C65D3B; }
.page.deco::after { content:""; position:absolute; left:17mm; right:17mm; top:11mm; height:1px; background:#CFC3AE; }
.btn { font-family:'Inter'; font-weight:600; font-size:13px; padding:11px 22px; border-radius:999px; background:#123B32; color:#F3EDE2; border:1.5px solid #123B32;
  display:inline-flex; gap:8px; align-items:center; position:relative; }
.btn.sec { background:transparent; color:#123B32; } .btn.fan { background:transparent; border-color:transparent; color:#123B32; padding-left:4px; padding-right:4px;
  border-radius:0; background-image:linear-gradient(#C65D3B,#C65D3B); background-size:0% 2px; background-position:0 100%; background-repeat:no-repeat; }
.btn.fan.hover { background-size:100% 2px; }
.btn.peligro { background:#C65D3B; border-color:#C65D3B; color:#fff; }
.btn.hover { background:#1C5245; box-shadow:0 6px 18px -8px rgba(18,59,50,.6); }
.btn.sec.hover { background:#DCE6DF; box-shadow:none; }
.btn.sec.press { background:#C9D7CD; }
.btn.fan.hover, .btn.fan.press, .btn.fan.foco { background-color:transparent; box-shadow:none; }
.btn.fan.press { color:#0D2C25; }
.btn.fan.foco { outline:2px solid #D9A441; outline-offset:3px; }
.btn.fan.dis { background-color:transparent; }
.btn.peligro.hover { background:#A94A2C; }
.btn.peligro.press { background:#8E3C22; }
.btn.press { transform:scale(.97); background:#0D2C25; }
.btn.dis { background:#E4D9C6; border-color:#E4D9C6; color:#9B9483; }
.btn.foco { box-shadow:0 0 0 3px #F3EDE2, 0 0 0 5px #D9A441; }
.chip { font-family:'Inter'; font-weight:600; font-size:10.5px; padding:4px 10px; border-radius:999px; display:inline-block; }
.chip.cu { background:#DCE6DF; color:#123B32; } .chip.pa { background:#F6E6C4; color:#7A5410; } .chip.ni { background:#ECE5D8; color:#6A675E; }
.campo { border:1px solid #CFC3AE; border-radius:10px; padding:10px 12px; font-size:12px; background:#FBF8F2; }
.campo.foco { border-color:#123B32; box-shadow:0 0 0 3px rgba(217,164,65,.35); }
.bar { height:6px; background:#E4D9C6; border-radius:3px; } .bar i { display:block; height:100%; background:#123B32; border-radius:3px; }
mark { background:linear-gradient(transparent 55%, rgba(217,164,65,.55) 55%); color:inherit; }
""",
    "C": """
:root { --paper:#0B0D17; --ink:#E7E9F5; --title:#FFFFFF; --muted:#9AA0BC; --surface:#161A2B; --line:#262B42;
  --fd:'Space Grotesk'; --ft:'Space Grotesk'; --fn:'JetBrains Mono'; --h2:42px; --wd:600; --ls:-.035em; --r:12px; --border:1px solid #262B42; --okt:#B8F35A;
  --prim:#7C5CFF; --sec:#22D3EE; --acc:#B8F35A; }
.page { background: radial-gradient(circle at 92% 0%, rgba(124,92,255,.22), transparent 42%), radial-gradient(circle at 0% 100%, rgba(34,211,238,.12), transparent 40%), #0B0D17; }
.page.deco::before { content:""; position:absolute; inset:0; background-image:linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
  background-size: 8mm 8mm; pointer-events:none; }
.page > *:not(.pie) { position:relative; }
.cab .num { color:#22D3EE; }
.btn { font-family:'Space Grotesk'; font-weight:600; font-size:13px; padding:11px 20px; border-radius:10px; color:#fff; border:1px solid rgba(255,255,255,.14);
  background:linear-gradient(135deg,#7C5CFF,#5B3FF0); display:inline-flex; gap:8px; align-items:center; box-shadow:inset 0 1px 0 rgba(255,255,255,.25); }
.btn.sec { background:#161A2B; border-color:#363C5C; } .btn.fan { background:transparent; border-color:transparent; box-shadow:none; color:#22D3EE; }
.btn.peligro { background:linear-gradient(135deg,#FF5C7A,#E23A5B); }
.btn.hover { box-shadow:0 0 0 1px rgba(124,92,255,.6), 0 8px 26px -6px rgba(124,92,255,.75), inset 0 1px 0 rgba(255,255,255,.3); }
.btn.sec.hover { border-color:#22D3EE; box-shadow:0 0 18px -4px rgba(34,211,238,.6); }
.btn.fan.hover { box-shadow:none; text-shadow:0 0 12px rgba(34,211,238,.8); }
.btn.fan.dis { background:transparent; border-color:transparent; }
.btn.press { transform:scale(.97); filter:brightness(.9); }
.btn.dis { background:#1C2033; color:#59607E; border-color:#262B42; box-shadow:none; }
.btn.foco { box-shadow:0 0 0 2px #0B0D17, 0 0 0 4px #22D3EE; }
.btn.carga { background:linear-gradient(110deg,#5B3FF0 30%,#9C85FF 50%,#5B3FF0 70%); }
.chip { font-family:'JetBrains Mono'; font-size:10px; padding:4px 9px; border-radius:6px; display:inline-block; border:1px solid; }
.chip.cu { color:#B8F35A; border-color:rgba(184,243,90,.4); background:rgba(184,243,90,.08); }
.chip.pa { color:#FFC14D; border-color:rgba(255,193,77,.4); background:rgba(255,193,77,.08); }
.chip.ni { color:#9AA0BC; border-color:#363C5C; }
.campo { border:1px solid #363C5C; border-radius:10px; padding:10px 12px; font-size:12px; background:#0F1220; color:#E7E9F5; }
.campo.foco { border-color:#22D3EE; box-shadow:0 0 0 3px rgba(34,211,238,.18); }
.bar { height:6px; background:#262B42; border-radius:3px; } .bar i { display:block; height:100%; border-radius:3px; background:linear-gradient(90deg,#7C5CFF,#22D3EE); box-shadow:0 0 10px rgba(34,211,238,.6); }
""",
}

# ------------------------------------------------------------------ piezas reutilizables
def pagina(m, n, titulo, cuerpo, deco=True, extra_cls=""):
    return (f'<section class="page {"deco" if deco else ""} {extra_cls}">'
            f'<div class="cab"><span class="num">{n:02d}</span><h2>{titulo}</h2></div>{cuerpo}'
            f'<div class="pie"><span>HireMind · Manual de marca · Propuesta {m} · {MARCAS[m]["nombre"]}</span><span>{n:02d}</span></div></section>')


def curva(x1, y1, x2, y2, color, ancho=120, alto=80):
    # y invertida; deja margen para rebotes > 1
    sy = lambda y: 70 - y * 55
    return (f'<svg viewBox="-6 -6 112 86" width="{ancho}" height="{alto}">'
            f'<rect x="0" y="15" width="100" height="55" fill="none" stroke="currentColor" stroke-opacity=".18"/>'
            f'<path d="M0 {sy(0)} C{x1*100} {sy(y1)} {x2*100} {sy(y2)} 100 {sy(1)}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
            f'<circle cx="0" cy="{sy(0)}" r="3" fill="{color}"/><circle cx="100" cy="{sy(1)}" r="3" fill="{color}"/></svg>')


def anillo(p, m, tam=70):
    r = 26
    c = 2 * 3.14159 * r
    col = {"A": "#2EE5A7", "B": "#123B32", "C": "#22D3EE"}[m]
    fondo = {"A": "#E6EDFF", "B": "#E4D9C6", "C": "#262B42"}[m]
    texto = {"A": "#0A0147", "B": "#123B32", "C": "#FFFFFF"}[m]
    fuente = {"A": "'Bebas Neue'", "B": "'Fraunces'", "C": "'JetBrains Mono'"}[m]
    sw = 9 if m == "A" else 6
    cap = "butt" if m == "A" else "round"
    return (f'<svg viewBox="0 0 64 64" width="{tam}" height="{tam}"><circle cx="32" cy="32" r="{r}" fill="none" stroke="{fondo}" stroke-width="{sw}"/>'
            f'<circle cx="32" cy="32" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="{cap}" '
            f'stroke-dasharray="{c:.1f}" stroke-dashoffset="{c*(1-p/100):.1f}" transform="rotate(-90 32 32)"/>'
            f'<text x="32" y="{37 if m=="A" else 36}" text-anchor="middle" font-family="{fuente}" font-size="{16 if m=="A" else 13}" font-weight="600" fill="{texto}">{p}</text></svg>')


CANDIDATOS = [("Andrea Salazar", 100, "cu cu cu cu cu"), ("Carlos Ortiz", 90, "cu cu cu cu ni"),
              ("María José Paredes", 87.5, "pa cu cu cu cu"), ("Luis Andrango", 57.5, "pa pa cu ni cu")]


def punto(e, m):
    col = {"A": {"cu": "#2EE5A7", "pa": "#FFB547", "ni": "#FFFFFF"},
           "B": {"cu": "#2F7D5B", "pa": "#D9A441", "ni": "#D4CAB7"},
           "C": {"cu": "#B8F35A", "pa": "#FFC14D", "ni": "#363C5C"}}[m][e]
    borde = "border:1.5px solid #0A0147;" if m == "A" else ""
    forma = "0" if m == "A" else "50%"
    return f'<i style="display:inline-block;width:9px;height:9px;border-radius:{forma};background:{col};{borde}margin-right:3px"></i>'


def maqueta_app(m, ancho="100%", n=4):
    """Pantalla de ranking con el estilo de la marca."""
    cfg = {"A": ("#FFFFFF", "#0A0147", "2.5px solid #0A0147", "0", "#D9FBEF"),
           "B": ("#FBF8F2", "#1B1B18", "1px solid #E1D8C8", "14px", "#EEF2EE"),
           "C": ("#11152A", "#E7E9F5", "1px solid #262B42", "12px", "rgba(124,92,255,.12)")}[m]
    fondo, tinta, borde, rad, sel = cfg
    filas = ""
    for i, (nom, p, est) in enumerate(CANDIDATOS[:n]):
        num_bg = {"A": "#FD696E", "B": "#123B32", "C": "#7C5CFF"}[m]
        num_fg = {"A": "#0A0147", "B": "#F3EDE2", "C": "#fff"}[m]
        numr = "0" if m == "A" else "50%"
        nb = "border:2px solid #0A0147;" if m == "A" else ""
        pf = {"A": "'Bebas Neue';font-size:20px", "B": "'Fraunces';font-size:16px;font-weight:600", "C": "'JetBrains Mono';font-size:13px"}[m]
        filas += (f'<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;{"background:"+sel+";" if i==0 else ""}border-bottom:{borde if m!="A" else "2px solid #0A0147"}">'
                  f'<span style="width:22px;height:22px;border-radius:{numr};background:{num_bg};color:{num_fg};{nb}display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700">{i+1}</span>'
                  f'<div style="flex:1"><div style="font-size:11.5px;font-weight:600;color:{tinta}">{nom}</div><div style="margin-top:3px">{"".join(punto(e, m) for e in est.split())}</div></div>'
                  f'<div style="width:70px;text-align:right"><div style="font-family:{pf};color:{tinta}">{str(p).replace(".", ",")}</div><div class="bar" style="margin-top:3px"><i style="width:{p}%"></i></div></div></div>')
    cab_bg = {"A": "#0A0147", "B": "#123B32", "C": "#0B0D17"}[m]
    cab = (f'<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:{cab_bg};border-bottom:{borde}">'
           f'{logo(m, 18, negativo=True)}<span style="font-size:9px;color:rgba(255,255,255,.7)">Asistente contable · Ranking</span></div>')
    return (f'<div style="width:{ancho};background:{fondo};border:{borde};border-radius:{rad};overflow:hidden;'
            f'{"box-shadow:6px 6px 0 #0A0147;" if m=="A" else "box-shadow:0 20px 40px -24px rgba(0,0,0,.45);" if m=="B" else "box-shadow:0 0 0 1px rgba(124,92,255,.25),0 24px 50px -20px rgba(124,92,255,.45);"}">{cab}{filas}</div>')


# ------------------------------------------------------------------ páginas
def p_portada(m):
    b = MARCAS[m]
    if m == "A":
        return f'''<section class="page" style="background:#2EE5A7;padding:0">
  <div style="position:absolute;top:0;left:120mm;width:70mm;height:14mm;background:#0A0147"></div>
  <div style="position:absolute;bottom:0;left:135mm;width:65mm;height:13mm;background:#0A0147"></div>
  <div style="position:absolute;left:0;top:0;bottom:0;width:98mm;background:#FFFFFF"></div>
  <div style="position:absolute;left:-28mm;bottom:-28mm;width:56mm;height:56mm;border-radius:50%;border:12mm solid #FD696E"></div>
  <div style="position:absolute;left:22mm;top:52mm">{simbolo("A", 210)}</div>
  <div style="position:absolute;left:112mm;top:38mm;right:16mm">
    <div style="font-family:'Bebas Neue';font-size:150px;line-height:.85;color:#FD696E">HIRE<br>MIND</div>
    <div style="font-family:'Bebas Neue';font-size:40px;color:#0A0147;margin-top:6mm;letter-spacing:.02em">MANUAL DE MARCA · PROPUESTA A</div>
    <div style="font-family:'Montserrat';font-weight:800;font-style:italic;font-size:15px;color:#0A0147;margin-top:2mm">“{b['nombre']}” — {b['subtitulo']}</div>
    <div style="font-family:'Montserrat';font-size:11px;color:#0A0147;margin-top:10mm;opacity:.8">{FECHA} · Para revisión y votación del grupo</div>
  </div></section>'''
    if m == "B":
        return f'''<section class="page" style="padding:0;background:#F3EDE2">
  <div style="position:absolute;right:0;top:0;bottom:0;width:112mm;background:#123B32;display:flex;align-items:center;justify-content:center">
    {simbolo("B", 250)}</div>
  <div style="position:absolute;left:20mm;top:22mm;font-family:'Inter';font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:#6A675E">Manual de marca · Propuesta B</div>
  <div style="position:absolute;left:20mm;top:58mm;width:150mm">
    <div style="font-family:'Fraunces';font-size:96px;line-height:.95;color:#123B32;letter-spacing:-.03em;font-variation-settings:'opsz' 144">Hire<em style="font-weight:400;color:#C65D3B">mind</em></div>
    <div style="width:30mm;height:3px;background:#D9A441;margin:9mm 0 7mm"></div>
    <div style="font-family:'Fraunces';font-size:26px;color:#1B1B18;font-style:italic">{b['tagline']}</div>
    <div style="font-family:'Inter';font-size:12px;color:#6A675E;margin-top:5mm">“{b['nombre']}” — {b['subtitulo']}</div>
  </div>
  <div style="position:absolute;left:20mm;bottom:16mm;font-family:'Inter';font-size:10.5px;color:#6A675E">{FECHA} · Para revisión y votación del grupo</div></section>'''
    return f'''<section class="page deco" style="padding:0">
  <div style="position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);width:150mm;height:150mm;border-radius:50%;
    background:radial-gradient(circle, rgba(124,92,255,.35), rgba(34,211,238,.08) 45%, transparent 70%)"></div>
  <div style="position:absolute;left:0;right:0;top:34mm;display:flex;flex-direction:column;align-items:center;text-align:center">
    <div style="filter:drop-shadow(0 0 24px rgba(124,92,255,.6))">{simbolo("C", 150)}</div>
    <div style="margin-top:8mm">{logotipo("C", 78, negativo=True)}</div>
    <div style="font-family:'Space Grotesk';font-size:20px;color:#9AA0BC;margin-top:5mm">{b['tagline']}</div>
  </div>
  <div style="position:absolute;left:17mm;right:17mm;bottom:14mm;display:flex;justify-content:space-between;font-family:'JetBrains Mono';font-size:10px;color:#9AA0BC">
    <span>MANUAL DE MARCA / PROPUESTA C / “{b['nombre'].upper()}”</span><span>{FECHA.upper()} · PARA VOTACIÓN DEL GRUPO</span></div></section>'''


def p_concepto(m, n):
    b = MARCAS[m]
    adj = "".join(f'<div class="card" style="padding:5mm"><div style="font-family:var(--fd);font-size:{26 if m=="A" else 20}px;color:var(--title);font-weight:var(--wd)">{a}</div>'
                  f'<p class="small" style="margin-top:2mm">{d}</p></div>' for a, d in b["adjetivos"])
    si = "".join(f'<li>{t}</li>' for t in b["decimos"])
    no = "".join(f'<li>{t}</li>' for t in b["nodecimos"])
    tag_style = {"A": "font-family:'Bebas Neue';font-size:44px;color:#FD696E;line-height:1",
                 "B": "font-family:'Fraunces';font-style:italic;font-size:30px;color:#123B32;line-height:1.15",
                 "C": "font-family:'Space Grotesk';font-size:30px;font-weight:600;line-height:1.1;background:linear-gradient(90deg,#B4A3FF,#22D3EE);-webkit-background-clip:text;color:transparent"}[m]
    cuerpo = f'''<div class="cols" style="grid-template-columns:1.15fr 1fr">
  <div><div class="eti">Idea central</div><p style="font-size:14px">{b['idea']}</p>
    <div class="eti" style="margin-top:8mm">Lema</div><div style="{tag_style}">{b['tagline']}</div>
    <div class="eti" style="margin-top:8mm">Personalidad</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:3mm">{adj}</div></div>
  <div><div class="eti">Tono de voz</div>
    <div class="card" style="margin-bottom:4mm"><div style="font-weight:700;font-size:12px;color:var(--okt);margin-bottom:2mm">✓ Así hablamos</div><ul style="font-size:12px;line-height:1.7;padding-left:4mm">{si}</ul></div>
    <div class="card"><div style="font-weight:700;font-size:12px;color:#D2283A;margin-bottom:2mm">✕ Así no</div><ul style="font-size:12px;line-height:1.7;padding-left:4mm">{no}</ul></div>
    <p class="small" style="margin-top:5mm">Regla de oro en todas las propuestas: la IA <b>ordena y justifica</b>; nunca “elige”, “descarta” ni “contrata”. La decisión es de una persona.</p></div></div>'''
    return pagina(m, n, "Concepto y tono" if m != "B" else "Concepto y <em>tono</em>", cuerpo)


def p_logo(m, n):
    fondo_logo = {"A": "#FFFFFF", "B": "#FBF8F2", "C": "#11152A"}[m]
    neg = m == "C"
    grid = ('<svg viewBox="0 0 64 64" width="190" height="190" style="position:absolute;inset:0;margin:auto">'
            + "".join(f'<line x1="{i*8}" y1="0" x2="{i*8}" y2="64" stroke="#FD696E" stroke-width=".25" opacity=".6"/>'
                      f'<line x1="0" y1="{i*8}" x2="64" y2="{i*8}" stroke="#FD696E" stroke-width=".25" opacity=".6"/>' for i in range(9))
            + '</svg>')
    construccion = {
        "A": "Una lupa que revisa y un check que confirma: el agente lee cada CV y marca lo que sí puede verificar. Trazos gruesos y esquinas rectas, como los bloques de la presentación. El cuadrado menta detrás es el “documento”.",
        "B": "Dos comillas: la cita textual que respalda cada dato del CV. Se dibujan como dos comas iguales sobre un cuadrado redondeado; la línea ocre es el resaltador que marca la evidencia.",
        "C": "Tres barras que crecen: el ranking. El punto sobre la barra más alta es una persona: quien revisa el top y toma la decisión final. Degradado violeta → cian que va del dato a la señal.",
    }[m]
    cuerpo = f'''<div class="cols" style="grid-template-columns:1.25fr 1fr">
  <div class="card" style="display:flex;align-items:center;justify-content:center;background:{fondo_logo}">{logo(m, 92, negativo=neg)}</div>
  <div style="display:flex;flex-direction:column;gap:5mm">
    <div><div class="eti">Concepto del símbolo</div><p>{construccion}</p></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:4mm">
      <div><div class="eti">Construcción · retícula 8×8</div>
        <div class="card" style="position:relative;height:52mm;display:flex;align-items:center;justify-content:center;padding:0">{simbolo(m, 190)}{grid}</div></div>
      <div><div class="eti">Área de protección</div>
        <div class="card" style="height:52mm;display:flex;align-items:center;justify-content:center;padding:0">
          <div style="padding:10px;outline:1.5px dashed #FD696E;outline-offset:0;position:relative">{simbolo(m, 70)}
            <span style="position:absolute;top:-15px;left:50%;transform:translateX(-50%);font-size:9px;color:#FD696E" class="mono">x</span>
            <span style="position:absolute;left:-12px;top:50%;transform:translateY(-50%);font-size:9px;color:#FD696E" class="mono">x</span></div></div>
        <p class="small" style="margin-top:2mm">x = ¼ del alto del símbolo. Nada entra en ese margen.</p></div></div>
    <div><div class="eti">Tamaño mínimo</div>
      <div style="display:flex;align-items:flex-end;gap:7mm">{logo(m, 24, negativo=neg)}<span class="small">Digital: 24 px de alto<br>Impreso: 8 mm de alto</span>{simbolo(m, 16)}<span class="small">Solo símbolo: 16 px</span></div></div>
  </div></div>'''
    return pagina(m, n, "Logo" if m != "B" else "El <em>logo</em>", cuerpo)


def p_versiones(m, n):
    oscuro = {"A": "#0A0147", "B": "#123B32", "C": "#0B0D17"}[m]
    claro = {"A": "#FFFFFF", "B": "#F3EDE2", "C": "#E7E9F5"}[m]
    marca = {"A": "#2EE5A7", "B": "#C65D3B", "C": "#7C5CFF"}[m]
    tinta = {"A": "#0A0147", "B": "#123B32", "C": "#0B0D17"}[m]
    def caja(contenido, bg, nombre, x=False):
        return (f'<div><div class="card {"x" if x else ""}" style="background:{bg};height:30mm;display:flex;align-items:center;justify-content:center;padding:0">{contenido}</div>'
                f'<div class="small" style="margin-top:1.5mm">{nombre}</div></div>')
    versiones = "".join([
        caja(logo(m, 34, negativo=(m == "C")), {"A": "#FFFFFF", "B": "#FBF8F2", "C": "#11152A"}[m], "Principal horizontal"),
        caja(logo(m, 30, negativo=True), oscuro if m != "C" else "#1A1640", "Negativo"),
        caja(logo(m, 34, color=tinta if m != "C" else "#0B0D17"), claro if m != "C" else "#E7E9F5", "Monocromo"),
        caja(logo(m, 26, apilado=True, negativo=(m == "C")), {"A": "#D9FBEF", "B": "#DCE6DF", "C": "#161A2B"}[m], "Apilado"),
    ])
    iconos = "".join(f'<div style="text-align:center">{simbolo(m, t)}<div class="small mono" style="margin-top:1mm">{t} px</div></div>' for t in (64, 40, 24, 16))
    mal = "".join([
        caja(f'<div style="transform:scaleX(1.6)">{logo(m, 26, negativo=(m=="C"))}</div>', "var(--surface)", "No deformar", True),
        caja(logo(m, 30, color="#2EA3E5" if m != "B" else "#7B3FA0"), "var(--surface)", "No cambiar los colores", True),
        caja(f'<div style="filter:drop-shadow(4px 6px 3px rgba(0,0,0,.55))">{logo(m, 30, negativo=(m=="C"))}</div>', "var(--surface)", "No agregar sombras ni efectos", True),
        caja(logo(m, 30, color=marca), marca if m != "C" else "#7C5CFF", "No usar sobre fondos sin contraste", True),
    ])
    cuerpo = f'''<div style="display:flex;flex-direction:column;gap:6mm;flex:1">
  <div><div class="eti">Versiones</div><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4mm">{versiones}</div></div>
  <div style="display:grid;grid-template-columns:1fr 2.2fr;gap:6mm">
    <div><div class="eti">Ícono de app y favicon</div><div class="card" style="display:flex;align-items:flex-end;justify-content:space-around;height:30mm">{iconos}</div></div>
    <div><div class="eti">Usos incorrectos</div><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4mm">{mal}</div></div></div></div>'''
    return pagina(m, n, "Versiones y usos" if m != "B" else "Versiones y <em>usos</em>", cuerpo)


def p_color(m, n):
    b = MARCAS[m]
    def texto_sobre(hexa):
        return "#FFFFFF" if contraste("#FFFFFF", hexa) >= contraste("#0B0D17", hexa) else "#0B0D17"
    sw = "".join(
        f'<div style="background:{h};color:{texto_sobre(h)};padding:5mm;display:flex;flex-direction:column;justify-content:space-between;'
        f'border-radius:var(--r);{"border:2.5px solid #0A0147;" if m=="A" else "border:1px solid rgba(0,0,0,.08);" if h in ("#FFFFFF","#F3EDE2") else ""}">'
        f'<div style="font-family:var(--fd);font-size:{24 if m=="A" else 17}px;font-weight:var(--wd)">{nom}</div>'
        f'<div style="font-size:10px;line-height:1.5"><b class="mono">{h}</b><br>RGB {rgb(h)}<br><span style="opacity:.8">{uso}</span></div></div>'
        for nom, h, uso, _ in b["colores"])
    prop = "".join(f'<div title="{nom}" style="flex:{p};background:{h};{"box-shadow:inset 0 0 0 1px rgba(0,0,0,.12);" if m=="B" else ""}{"border-right:2px solid #0A0147;" if m=="A" else ""}"></div>' for nom, h, _, p in b["colores"])
    apoyo = "".join(f'<div style="display:flex;align-items:center;gap:2.5mm"><span style="width:9mm;height:9mm;border-radius:calc(var(--r)*.5);background:{h};'
                    f'border:1px solid rgba(128,128,128,.25)"></span><span class="small"><b style="color:var(--ink)">{nom}</b><br><span class="mono">{h}</span></span></div>'
                    for nom, h in b["apoyo"])
    filas = ""
    for fg, bg in b["pares"]:
        r = contraste(fg, bg)
        nv = nivel(r)
        cls = "no" if nv == "No apto" else "ok"
        filas += (f'<tr><td><span style="display:inline-block;padding:3px 10px;background:{bg};color:{fg};border-radius:4px;font-weight:600;'
                  f'border:1px solid rgba(128,128,128,.25)">Aa texto</span></td><td class="mono">{fg} / {bg}</td>'
                  f'<td class="mono">{r:.1f}:1</td><td class="{cls}">{nv}</td></tr>')
    cuerpo = f'''<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:3mm;height:52mm">{sw}</div>
  <div style="display:grid;grid-template-columns:1fr 1.25fr;gap:8mm;margin-top:6mm;flex:1">
    <div><div class="eti">Proporción de uso</div><div style="display:flex;height:9mm;border-radius:var(--r);overflow:hidden;{"border:2.5px solid #0A0147" if m=="A" else ""}">{prop}</div>
      <div class="eti" style="margin-top:6mm">Colores de apoyo</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:3mm">{apoyo}</div></div>
    <div><div class="eti">Contraste (WCAG 2.1, calculado)</div><table><tr><th>Muestra</th><th>Texto / fondo</th><th>Relación</th><th>Nivel</th></tr>{filas}</table>
      <p class="small" style="margin-top:2mm">AA exige 4,5:1 para texto normal y 3:1 para texto grande (≥ 24 px).</p></div></div>'''
    return pagina(m, n, "Color" if m != "B" else "<em>Color</em>", cuerpo)


def p_tipo(m, n):
    b = MARCAS[m]
    escala = {
        "A": [("Display", "'Bebas Neue'", 64, 400, "SIN SESGOS", "1,0"), ("Título 1", "'Bebas Neue'", 40, 400, "TOP 5 LISTO", "1,0"),
              ("Título 2", "'Montserrat'", 22, 800, "Asistente contable", "1,2"), ("Cuerpo", "'Montserrat'", 15, 500, "Cumple con formación y experiencia contable.", "1,55"),
              ("Etiqueta", "'Montserrat'", 12, 800, "EVIDENCIA VERIFICADA", "1,3")],
        "B": [("Display", "'Fraunces'", 60, 600, "Con evidencia", "1,0"), ("Título 1", "'Fraunces'", 38, 600, "Ranking de candidatos", "1,1"),
              ("Título 2", "'Inter'", 22, 600, "Asistente contable", "1,25"), ("Cuerpo", "'Inter'", 15, 400, "Cumple con formación y experiencia contable.", "1,6"),
              ("Etiqueta", "'Inter'", 12, 600, "Evidencia verificada", "1,4")],
        "C": [("Display", "'Space Grotesk'", 60, 600, "Señal clara", "1,0"), ("Título 1", "'Space Grotesk'", 38, 600, "Ranking · 7 CV", "1,1"),
              ("Título 2", "'Space Grotesk'", 22, 500, "Asistente contable", "1,25"), ("Cuerpo", "'Space Grotesk'", 15, 400, "Cumple con formación y experiencia contable.", "1,55"),
              ("Dato", "'JetBrains Mono'", 13, 400, "puntaje 87,5 · 9,4 s · p95 11,4 s", "1,4")],
    }[m]
    filas = "".join(f'<tr><td style="width:24mm" class="small">{nom}<br><span class="mono">{t}px · {w}</span></td>'
                    f'<td style="font-family:{f};font-size:{t}px;font-weight:{w};line-height:{lh.replace(",", ".")};color:var(--title)">{ej}</td></tr>'
                    for nom, f, t, w, ej, lh in escala)
    alf = "Aa Bb Cc Dd Ee Ff Gg Hh Ii Jj Kk Ll Mm Nn Ññ Oo Pp Qq Rr Ss Tt Uu Vv Ww Xx Yy Zz<br>0 1 2 3 4 5 6 7 8 9 · á é í ó ú ü ¿? ¡! % ·"
    def ficha(fam, desc, peso):
        return (f'<div class="card"><div class="small">{"Display" if fam == b["fuente_d"] else "Texto y datos"}</div>'
                f'<div style="font-family:\'{fam}\';font-size:38px;font-weight:{peso};color:var(--title);line-height:1.1;margin:1mm 0 2mm">{fam}</div>'
                f'<p class="small">{desc}</p><div style="font-family:\'{fam}\';font-size:12px;line-height:1.6;margin-top:3mm;color:var(--ink)">{alf}</div></div>')
    segunda = b["fuente_n"] if m == "C" else b["fuente_t"]
    cuerpo = f'''<div class="cols" style="grid-template-columns:1fr 1.3fr">
  <div style="display:flex;flex-direction:column;gap:4mm">{ficha(b["fuente_d"], b["desc_d"], 600 if m!="A" else 400)}{ficha(segunda, b["desc_t"], 500)}</div>
  <div><div class="eti">Escala tipográfica (pantalla)</div><table>{filas}</table>
    <p class="small" style="margin-top:3mm">Todas las fuentes son gratuitas (Google Fonts, licencia OFL) y se pueden instalar en la app sin internet.</p></div></div>'''
    return pagina(m, n, "Tipografía" if m != "B" else "<em>Tipografía</em>", cuerpo)


def p_componentes(m, n):
    icono = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    spinner = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M12 3a9 9 0 1 0 9 9" stroke-linecap="round"/></svg>')
    estados = [("Normal", ""), ("Hover", "hover"), ("Presionado", "press"), ("Foco teclado", "foco"), ("Deshabilitado", "dis")]
    tipos = [("Principal", "", f"Evaluar {icono}"), ("Secundario", "sec", "Subir CV"), ("Texto", "fan", "Ver detalle"), ("Peligro", "peligro", "Eliminar")]
    cab = "".join(f'<th style="text-align:center">{e}</th>' for e, _ in estados)
    filas = ""
    for nom, cls, txt in tipos:
        celdas = "".join(f'<td style="text-align:center;padding:4mm 1mm"><span class="btn {cls} {ec}">{txt}</span></td>' for _, ec in estados)
        filas += f'<tr><td class="small" style="width:22mm"><b style="color:var(--ink)">{nom}</b></td>{celdas}</tr>'
    carga = "carga" if m == "C" else ""
    tarjeta = maqueta_app(m, n=2 if m == "A" else 3)
    cuerpo = f'''<div class="cols" style="grid-template-columns:1.45fr 1fr">
  <div><div class="eti">Botones · tipos y estados</div><table><tr><th></th>{cab}</tr>{filas}</table>
    <div style="display:flex;gap:6mm;align-items:center;margin-top:4mm"><span class="btn {carga}">{spinner} Evaluando 3 de 7…</span>
      <span class="small">Cargando: el texto cambia y aparece el indicador; el botón no cambia de tamaño.</span></div></div>
  <div style="display:flex;flex-direction:column;gap:4mm">
    <div><div class="eti">Estados de un criterio</div><div style="display:flex;gap:2mm;flex-wrap:wrap">
      <span class="chip cu">✓ Cumple</span><span class="chip pa">◐ Parcial</span><span class="chip ni">○ No identificado</span></div></div>
    <div><div class="eti">Campo de texto</div><div class="campo">Asistente contable</div><div class="campo foco" style="margin-top:2mm">Excel avanzado|</div></div>
    <div><div class="eti">Barra de puntaje</div><div class="bar"><i style="width:87.5%"></i></div></div>
    <div><div class="eti">Lista de ranking</div>{tarjeta}</div></div></div>'''
    return pagina(m, n, "Botones y componentes" if m != "B" else "Botones y <em>componentes</em>", cuerpo)


# --------------------------------------------------- storyboards (cuadros de animación)
def _frames(cuadros, tiempos):
    return ('<div class="frames">' + "".join(f'<div><div class="frame">{c}</div><div class="frame-t">{t}</div></div>' for c, t in zip(cuadros, tiempos)) + "</div>")


def sb_logo(m):
    if m == "A":
        cuadros = []
        for k in range(5):
            mint = '<rect x="10" y="10" width="50" height="50" fill="#2EE5A7"/>' if k >= 1 else ""
            dx = [0, -30, -8, 2, 0][k]
            lente = (f'<g transform="translate({dx},0)"><circle cx="27" cy="27" r="16" fill="#fff" stroke="#0A0147" stroke-width="7"/>'
                     f'<path d="M39 39 L55 55" stroke="#0A0147" stroke-width="9"/></g>') if k >= 1 else ""
            chk = '<path d="M19 27.5 l6 6 l10.5 -12" fill="none" stroke="#FD696E" stroke-width="5.5" stroke-dasharray="30" stroke-dashoffset="{}"/>'.format([30, 30, 30, 14, 0][k])
            esc = [0.2, 1, 1, 1, 1][k]
            cuadros.append(f'<svg viewBox="0 0 64 64" width="80" height="80"><g transform="translate(32 32) scale({esc}) translate(-32 -32)">'
                           f'{mint if k else "<rect x=26 y=26 width=12 height=12 fill=#2EE5A7 />"}{lente}{chk if k>=2 else ""}</g></svg>')
        return "Logo · entrada", "960 ms", _frames(cuadros, ["0 ms · bloque", "240 · lupa entra", "480 · rebote", "720 · check", "960 · fin"])
    if m == "B":
        cuadros = []
        for k in range(5):
            op1 = [0, 1, 1, 1, 1][k]; op2 = [0, 0, 1, 1, 1][k]; y1 = [8, 0, 0, 0, 0][k]; y2 = [8, 8, 0, 0, 0][k]
            linea = [0, 0, 0, 16, 32][k]
            coma = lambda dx, op, y: (f'<g opacity="{op}" transform="translate(0 {y})"><circle cx="{22+dx}" cy="38" r="7.5" fill="#F3EDE2"/>'
                                      f'<path d="M{14.6+dx} 38.5 C{14.2+dx} 28 {18+dx} 21 {27+dx} 17.5 L{28.6+dx} 21 C{22.5+dx} 24 {20.6+dx} 29 {21+dx} 33 Z" fill="#F3EDE2"/></g>')
            cuadros.append(f'<svg viewBox="0 0 64 64" width="78" height="78"><rect width="64" height="64" rx="16" fill="#123B32" opacity="{[.4,1,1,1,1][k]}"/>'
                           f'{coma(0, op1, y1)}{coma(19, op2, y2)}<rect x="16" y="49" width="{linea}" height="3.2" rx="1.6" fill="#D9A441"/></svg>')
        return "Logo · entrada", "900 ms", _frames(cuadros, ["0 ms · fundido", "200 · 1.ª comilla", "380 · 2.ª comilla", "640 · resaltador", "900 · fin"])
    cuadros = []
    for k in range(5):
        hs = [[0, 0, 0], [8, 0, 0], [20, 14, 0], [20, 30, 30], [20, 30, 36]][k]
        ys = [56 - h for h in hs]
        dot = '<circle cx="50" cy="9.5" r="6" fill="#22D3EE" opacity="{}"/>'.format([0, 0, 0, .4, 1][k])
        glow = ' style="filter:drop-shadow(0 0 6px rgba(34,211,238,.9))"' if k == 4 else ""
        cuadros.append(f'<svg viewBox="0 0 64 64" width="78" height="78"{glow}><defs><linearGradient id="sg{k}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#7C5CFF"/><stop offset="1" stop-color="#22D3EE"/></linearGradient></defs>'
                       + "".join(f'<rect x="{x}" y="{y}" width="12" height="{max(h, .01)}" rx="6" fill="url(#sg{k})" opacity="{o}"/>' for x, y, h, o in zip((8, 26, 44), ys, hs, (.55, .8, 1)))
                       + dot + "</svg>")
    return "Logo · carga del ranking", "1 100 ms", _frames(cuadros, ["0 ms", "180 · barra 1", "420 · barra 2", "700 · barra 3", "1 100 · persona + brillo"])


def sb_boton(m):
    estados = [("", "Reposo"), ("hover", "Hover"), ("press", "Presión"), ("", "Soltar"), ("foco", "Foco")]
    tiempos = {"A": ["0 ms", "120 ms · sube 1 px", "90 ms · se hunde 4 px", "160 ms · rebota", "anillo azul"],
               "B": ["0 ms", "200 ms · se oscurece", "100 ms · escala 0,97", "200 ms · vuelve", "anillo ocre"],
               "C": ["0 ms", "180 ms · brillo violeta", "90 ms · escala 0,97", "180 ms · vuelve", "anillo cian"]}[m]
    cuadros = [f'<span class="btn {c}">Evaluar</span>' for c, _ in estados]
    return "Botón principal · interacción", "≈ 450 ms", _frames(cuadros, [f"{e} · {t}" for (_, e), t in zip(estados, tiempos)])


def sb_puntaje(m):
    vals = [0, 30, 62, 84, 87.5]
    cuadros = [anillo(v if v != 87.5 else 87.5, m) for v in vals]
    cuadros = [c.replace(">87.5<", ">87,5<") for c in cuadros]
    nombre = {"A": "Puntaje · llenado con rebote", "B": "Puntaje · trazo continuo", "C": "Puntaje · conteo de cifras"}[m]
    dur = {"A": "700 ms", "B": "800 ms", "C": "900 ms"}[m]
    return nombre, dur, _frames(cuadros, ["0 ms", "150 ms", "350 ms", "550 ms", f"{dur} · valor final"])


def sb_cv(m):
    cuadros = []
    for k in range(5):
        if m == "A":
            x = [-60, -10, 0, 0, 0][k]
            check = '<div style="position:absolute;right:-8px;top:-8px;width:22px;height:22px;background:#2EE5A7;border:2px solid #0A0147;font-size:12px;font-weight:800;display:flex;align-items:center;justify-content:center">✓</div>' if k == 4 else ""
            lupa = f'<div style="position:absolute;left:{[0,0,4,30,30][k]}px;top:{[0,0,6,26,26][k]}px;opacity:{[0,0,1,1,0][k]}">{simbolo("A", 26, fondo=False)}</div>'
            cuadros.append(f'<div style="position:relative;width:52px;height:66px;background:#fff;border:2.5px solid #0A0147;transform:translateX({x}px)">'
                           + "".join(f'<div style="height:4px;background:#0A0147;opacity:.25;margin:7px 6px 0;width:{w}%"></div>' for w in (70, 85, 55, 80, 60))
                           + lupa + check + "</div>")
        elif m == "B":
            w = [0, 30, 60, 100, 100][k]
            cuadros.append(f'<div style="width:118px;font-family:Inter;font-size:10px;line-height:1.5;color:#1B1B18;text-align:left">'
                           f'<span style="background:linear-gradient(90deg,rgba(217,164,65,.6) {w}%,transparent {w}%)">«Excel avanzado (tablas dinámicas)»</span>'
                           f'{"<div style=margin-top:4px><span class=chip cu>✓ Cumple</span></div>" if k==4 else ""}</div>')
        else:
            y = [0, 18, 38, 58, 70][k]
            cuadros.append(f'<div style="position:relative;width:52px;height:66px;background:#161A2B;border:1px solid #363C5C;border-radius:6px;overflow:hidden">'
                           + "".join(f'<div style="height:4px;border-radius:2px;background:{"#22D3EE" if (k and 7+i*11 < y) else "#363C5C"};opacity:{.9 if (k and 7+i*11<y) else 1};margin:7px 6px 0;width:{w}%"></div>' for i, w in enumerate((70, 85, 55, 80, 60)))
                           + (f'<div style="position:absolute;left:0;right:0;top:{y}px;height:2px;background:#22D3EE;box-shadow:0 0 10px 2px rgba(34,211,238,.8)"></div>' if k < 4 else
                              '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(11,13,23,.6);font-family:JetBrains Mono;font-size:11px;color:#B8F35A">9,4 s</div>')
                           + "</div>")
    nombre = {"A": "Hoja de vida · entra y se revisa", "B": "Evidencia · resaltador sobre la cita", "C": "Hoja de vida · escaneo"}[m]
    dur = {"A": "1 200 ms", "B": "600 ms", "C": "1 400 ms (en bucle mientras procesa)"}[m]
    tiempos = {"A": ["0 ms · fuera", "180 · desliza", "360 · lupa", "800 · revisa", "1 200 · ✓"],
               "B": ["0 ms", "150", "300", "600 · cita marcada", "+ estado"],
               "C": ["0 ms", "350", "700", "1 050", "fin · tiempo"]}[m]
    return nombre, dur, _frames(cuadros, tiempos)


def p_movimiento1(m, n):
    b = MARCAS[m]
    col = {"A": "#FD696E", "B": "#C65D3B", "C": "#22D3EE"}[m]
    pr = "".join(f'<div class="card" style="padding:4.5mm"><div style="font-family:var(--fd);font-size:{24 if m=="A" else 17}px;font-weight:var(--wd);color:var(--title)">{t}</div>'
                 f'<p class="small" style="margin-top:1.5mm">{d}</p></div>' for t, d in b["principios"])
    ease = "".join(f'<div class="card" style="padding:4mm;display:flex;gap:4mm;align-items:center;color:var(--ink)">{curva(x1, y1, x2, y2, col, 92, 66)}'
                   f'<div><b style="font-size:12px">{nom}</b><div class="mono small">{css}</div><div class="mono small" style="color:{col}">{dur}</div></div></div>'
                   for nom, css, x1, y1, x2, y2, dur in b["easings"])
    t, d, fr = sb_logo(m)
    cuerpo = f'''<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm">{pr}</div>
  <div class="eti" style="margin-top:5mm">Curvas y duraciones (tokens)</div><div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm">{ease}</div>
  <div style="margin-top:5mm"><div class="sb-tit"><b>{t}</b><span>{d}</span></div>{fr}</div>'''
    return pagina(m, n, "Movimiento" if m != "B" else "<em>Movimiento</em>", cuerpo)


def p_movimiento2(m, n):
    bloques = ""
    for fn in (sb_boton, sb_puntaje, sb_cv):
        t, d, fr = fn(m)
        bloques += f'<div><div class="sb-tit"><b>{t}</b><span>{d}</span></div>{fr}</div>'
    nota = ("Accesibilidad: si el sistema tiene activado “reducir movimiento”, las animaciones se reemplazan por un fundido de 120 ms.")
    cuerpo = f'<div style="display:flex;flex-direction:column;gap:5mm">{bloques}</div><p class="small" style="margin-top:4mm">{nota}</p>'
    return pagina(m, n, "Animaciones de la app" if m != "B" else "Animaciones de la <em>app</em>", cuerpo)


def p_aplicaciones(m, n):
    b = MARCAS[m]
    if m == "A":
        slide = ('<div style="aspect-ratio:16/9;background:#2EE5A7;position:relative;overflow:hidden;border:2.5px solid #0A0147">'
                 '<div style="position:absolute;top:0;right:12%;width:30%;height:9%;background:#0A0147"></div>'
                 '<div style="position:absolute;left:0;top:0;bottom:0;width:34%;background:#fff;display:flex;align-items:center;justify-content:center">' + simbolo("A", 80) + '</div>'
                 '<div style="position:absolute;left:40%;top:22%;font-family:Bebas Neue;font-size:44px;line-height:.85;color:#FD696E">HIRE<br>MIND</div>'
                 '<div style="position:absolute;left:40%;bottom:14%;font-family:Montserrat;font-weight:800;font-style:italic;font-size:10px;color:#0A0147">CONTRATA CON CRITERIO, NO A CIEGAS.</div></div>')
        post = ('<div style="aspect-ratio:1;background:#0A0147;padding:9%;display:flex;flex-direction:column;justify-content:space-between;border:2.5px solid #0A0147">'
                '<div style="font-family:Bebas Neue;font-size:40px;line-height:.9;color:#2EE5A7">100 CV.<br><span style="color:#FD696E">TU TOP 5.</span><br><span style="color:#fff">TÚ DECIDES.</span></div>'
                + logo("A", 20, negativo=True) + "</div>")
    elif m == "B":
        slide = ('<div style="aspect-ratio:16/9;background:#F3EDE2;position:relative;overflow:hidden;border:1px solid #E1D8C8;border-radius:10px">'
                 '<div style="position:absolute;right:0;top:0;bottom:0;width:36%;background:#123B32;display:flex;align-items:center;justify-content:center">' + simbolo("B", 84) + '</div>'
                 '<div style="position:absolute;left:7%;top:26%;font-family:Fraunces;font-size:32px;color:#123B32;letter-spacing:-.03em">Hire<em style="font-weight:400;color:#C65D3B">mind</em></div>'
                 '<div style="position:absolute;left:7%;top:56%;width:52%;font-family:Fraunces;font-style:italic;font-size:12px;color:#1B1B18">Cada decisión, con su evidencia.</div></div>')
        post = ('<div style="aspect-ratio:1;background:#123B32;padding:9%;display:flex;flex-direction:column;justify-content:space-between;border-radius:10px">'
                '<div style="font-family:Fraunces;font-size:24px;line-height:1.2;color:#F3EDE2">«No sabemos por qué quedó primero» <em style="color:#D9A441">ya no es una respuesta.</em></div>'
                + logo("B", 20, negativo=True) + "</div>")
    else:
        slide = ('<div style="aspect-ratio:16/9;background:radial-gradient(circle at 70% 30%,rgba(124,92,255,.45),transparent 55%),#0B0D17;position:relative;overflow:hidden;border:1px solid #262B42;border-radius:10px;'
                 'display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px">' + simbolo("C", 64) + logotipo("C", 36, negativo=True)
                 + '<div style="font-family:JetBrains Mono;font-size:9px;color:#9AA0BC">SEÑAL CLARA ENTRE CIENTOS DE CV</div></div>')
        post = ('<div style="aspect-ratio:1;background:#0B0D17;border:1px solid #262B42;border-radius:10px;padding:9%;display:flex;flex-direction:column;justify-content:space-between">'
                '<div><div style="font-family:JetBrains Mono;font-size:11px;color:#22D3EE">// 14 CV procesados</div>'
                '<div style="font-family:Space Grotesk;font-weight:600;font-size:46px;color:#fff;letter-spacing:-.04em">9,4 s</div><div style="font-family:Space Grotesk;font-size:13px;color:#9AA0BC">por hoja de vida, sin salir de la oficina.</div></div>'
                + logo("C", 20, negativo=True) + "</div>")
    cuerpo = f'''<div class="cols" style="grid-template-columns:1.25fr 1fr .75fr;align-items:start">
  <div><div class="eti">Interfaz de la app</div>{maqueta_app(m)}<p class="small" style="margin-top:3mm">Así se vería la pantalla de ranking con esta marca.</p></div>
  <div><div class="eti">Portada de presentación</div>{slide}</div>
  <div><div class="eti">Publicación para redes</div>{post}</div></div>'''
    return pagina(m, n, "Aplicaciones" if m != "B" else "<em>Aplicaciones</em>", cuerpo)


def p_voto(m, n):
    b = MARCAS[m]
    colores = "".join(f'<span style="display:inline-block;width:12mm;height:12mm;background:{h};border-radius:calc(var(--r)*.5);border:1px solid rgba(128,128,128,.3);margin-right:2mm"></span>' for _, h, _, _ in b["colores"])
    caja = f'<span style="display:inline-block;width:6mm;height:6mm;border:2px solid var(--ink);border-radius:{1 if m!="B" else 3}px;margin-right:3mm;vertical-align:middle"></span>'
    cuerpo = f'''<div class="cols" style="grid-template-columns:1fr 1fr">
  <div style="display:flex;flex-direction:column;gap:5mm">
    <div class="card" style="display:flex;align-items:center;justify-content:center;height:46mm">{logo(m, 64, negativo=(m=="C"))}</div>
    <div><div class="eti">En resumen</div><p><b>{b["nombre"]}</b> · {b["subtitulo"]}.<br>{b["tagline"]}</p></div>
    <div>{colores}</div>
    <div class="small">Tipografías: {b["fuente_d"]}{" + " + b["fuente_t"] if b["fuente_t"] != b["fuente_d"] else ""}{" + " + b["fuente_n"] if b["fuente_n"] not in (b["fuente_t"], b["fuente_d"]) else ""}</div>
    <div style="display:flex;gap:3mm"><span class="btn">Evaluar</span><span class="btn sec">Subir CV</span><span class="chip cu" style="align-self:center">✓ Cumple</span></div></div>
  <div class="card" style="display:flex;flex-direction:column;gap:5mm">
    <div style="font-family:var(--fd);font-size:{34 if m=="A" else 26}px;font-weight:var(--wd);color:var(--title)">Ficha de votación</div>
    <div style="font-size:13px;line-height:2.3">{caja}Apruebo esta propuesta<br>{caja}Me gusta, con cambios<br>{caja}Prefiero otra propuesta</div>
    <div><div class="eti">¿Qué cambiarías?</div>{"".join('<div style="border-bottom:1px solid var(--line);height:9mm"></div>' for _ in range(4))}</div>
    <div class="small">Nombre: ______________________________</div>
    <p class="small">Después de la votación, la propuesta ganadora se aplica a la app (logo, colores, botones y animaciones), a la landing y a las diapositivas.</p></div></div>'''
    return pagina(m, n, "Votación del grupo" if m != "B" else "Votación del <em>grupo</em>", cuerpo)


def documento(m: str) -> str:
    b = MARCAS[m]
    paginas = [p_portada(m)]
    for i, fn in enumerate([p_concepto, p_logo, p_versiones, p_color, p_tipo, p_componentes, p_movimiento1, p_movimiento2, p_aplicaciones, p_voto], start=2):
        paginas.append(fn(m, i))
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Manual de marca HireMind · Propuesta {m}</title>'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="https://fonts.googleapis.com/css2?{b["gfonts"]}&display=block" rel="stylesheet">'
            f'<style>{CSS_BASE}{CSS_MARCA[m]}</style></head><body>{"".join(paginas)}</body></html>')


def a_pdf(html: Path, pdf: Path):
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=15000", f"--print-to-pdf={pdf}", html.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)


if __name__ == "__main__":
    import sys
    HTML.mkdir(exist_ok=True)
    marcas = sys.argv[1:] or list(MARCAS)
    for m in marcas:
        h = HTML / f"{MARCAS[m]['archivo']}.html"
        h.write_text(documento(m), encoding="utf-8")
        p = AQUI / f"{MARCAS[m]['archivo']}.pdf"
        a_pdf(h, p)
        print(p.name, p.stat().st_size // 1024, "KB")
