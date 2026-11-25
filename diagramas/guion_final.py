"""Genera el guion de la exposición final (HTML) con miniaturas de las 29 diapositivas.

Uso: python3 guion_final.py <carpeta_miniaturas s-01.png...> <salida.html>
"""
import base64, pathlib, re, sys

TH = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])

# (título, minutos, [párrafos]); **negrita** marca las frases clave
SL = [
("HireMind", "0:30", [
"Buenos días. Somos el grupo 5 y les presentamos la versión final de **HireMind**, un agente de inteligencia artificial que ayuda a las **PYMEs ecuatorianas** a preseleccionar hojas de vida.",
"El agente lee los CV, los compara con lo que pide la vacante y entrega un **ranking justificado con evidencias**. Todo corre **en el computador de la empresa** y **la decisión final la toma una persona**.",
"El orden es: problema, cómo está construido, qué tan bien funciona según nuestra evaluación, el negocio y, al final, riesgos y conclusiones.",
]),
("Muchos postulantes y talento difícil de hallar", "0:45", [
"Ecuador tiene una **tasa de desempleo del 3,1 %** en 2026, pero el **52,8 % de los desempleados ha tenido empleos informales** y el **36 % no tiene experiencia** formal (Primicias).",
"Para quien contrata, eso significa **muchos postulantes con perfiles muy distintos**. Además, el **54 % de los expertos en RR. HH. busca habilidades blandas** (El Diario, 2025), y esas son difíciles de ver en un CV leído a la rápida.",
]),
("Contratar con poco tiempo y sin criterio sale caro", "0:45", [
"**Afectado:** PYMEs **sin departamento de recursos humanos**, donde contrata el dueño o el administrador.",
"**Problema:** los CV se **revisan a mano, sin criterios consistentes** y con poco tiempo. **Consecuencias:** procesos lentos, decisiones inconsistentes y **riesgo de una mala contratación**, que para una empresa pequeña sale cara.",
]),
("Arquitectura completa del agente", "1:30", [
"Todo vive dentro de este recuadro: **el equipo local de la PYME, con 16 GB de RAM**. **Los CV no salen a internet**.",
"Arriba está la **interfaz web en React**: panel, vacantes, carga de hojas de vida y ranking. Se comunica por una **API REST en FastAPI** con el **núcleo del agente en Python**, que tiene seis módulos: **ingesta** de PDF con PyMuPDF, **cliente LLM**, **validador** del JSON, **verificador de evidencia**, **filtro de equidad** y **motor de puntuación**.",
"A la derecha, **LM Studio** sirve el modelo **Qwen3-4B-Instruct** de forma local. **El modelo solo extrae datos y redacta la justificación: no pone la nota.** Todo se guarda en **SQLite**. Si hace falta más capacidad, se puede escalar a un modelo de 8B o a Gemini en la nube sin tocar el resto.",
"Cambio respecto al primer entregable: **la interfaz pasó de Streamlit a React + FastAPI**, que es más rápida y nos permitió aplicar la marca.",
]),
("Flujo de razonamiento del agente", "1:30", [
"Las tres franjas dicen quién hace qué: **el LLM extrae y redacta, Python valida y puntúa, la persona decide**.",
"Se lee el PDF; si no tiene texto, por ejemplo un escaneado, **pasa a revisión manual, no se descarta**. El modelo convierte el CV a JSON y **por cada dato copia la frase exacta del CV que lo respalda**. Si el JSON sale mal se reintenta con el error, máximo dos veces.",
"Python **busca cada cita en el CV**: si no existe, el dato queda \"no verificado\" y **vale cero**, así el modelo no puede inventar. Luego se excluyen datos personales, se compara con los criterios y se calcula **Σ peso × cumplimiento**. Al final el modelo redacta la justificación **solo con evidencias verificadas**.",
]),
("Criterios de selección del LLM", "1:00", [
"Elegimos un modelo **Qwen de 4B** por siete criterios: **español**, **extracción de información**, **salida JSON**, comparación con evidencia, **velocidad local**, **API compatible con OpenAI** y **100 % de privacidad**.",
"En memoria, el modelo ocupa entre **1,8 y 2,5 GB** y la ventana de contexto entre **0,8 y 1,5 GB**, así que **cabe en un computador de oficina de 16 GB**. Si se necesita más razonamiento, se sube a un 7B u 8B local, o a Gemini Flash en la nube.",
]),
("Herramientas y su rol", "0:45", [
"Cuatro capas y **todo es código abierto**. **Interfaz:** React 19 con Vite, Tailwind y TanStack Query. **Servicio:** FastAPI, Pydantic para el esquema JSON estricto y pytest para las pruebas. **Agente:** Python, PyMuPDF y el SDK de OpenAI como cliente. **Modelo y datos:** LM Studio, Qwen3-4B cuantizado a 4 bits y SQLite.",
"El criterio fue **reducir complejidad**: nada de servidores externos, para que se pueda instalar en cualquier PYME.",
]),
("Flujo de trabajo y evaluación responsable", "0:45", [
"Para el usuario son ocho pasos: **iniciar LM Studio, crear la vacante con sus pesos, subir los CV, revisar el ranking y elegir a quién entrevistar**; lo demás lo hace el agente.",
"El paso 8 es nuevo: al **elegir un candidato**, el agente le envía un **correo** y prepara **preguntas para la entrevista**.",
"Cuatro principios: **sin datos sensibles**, **evidencia verificable**, **el LLM no pone la nota** y **decisión humana**: nadie se descarta automáticamente.",
]),
("Métricas y protocolo de evaluación", "0:45", [
"En el entregable anterior nos comprometimos con estas metas: **F1 ≥ 0,90** en extracción, **NDCG@5 ≥ 0,85** en el ranking, **≤ 15 s por CV**, **100 % de JSON válido** y ningún sesgo. Ahora mostramos si las cumplimos.",
]),
("Resultados de la evaluación", "1:30", [
"Corrimos el agente **3 veces sobre 15 CV ficticios y 2 vacantes**: 210 criterios evaluados, con Qwen3-4B en una GPU de 8 GB. La referencia la **etiquetó a mano el equipo**.",
"**Exactitud por criterio: 100 %** y **F1 macro 1,00** (meta 0,90). **NDCG@5 promedio 0,98** (meta 0,85). **JSON válido al primer intento: 100 %**. **Tiempo: 9,5 s en promedio y 12 s en el P95** (meta 15 s). **Equidad: 24 de 24** variantes sin cambio de puntaje.",
"Una aclaración honesta: **15 CV es un conjunto pequeño y los armamos nosotros**. Los resultados muestran que el diseño funciona, pero **falta validarlo con CV reales de PYMEs**. El script es reproducible: hiremind/scripts/evaluar.py.",
]),
("Prueba con CV del grupo", "1:00", [
"Además del set etiquetado, cada integrante consiguió hojas de vida reales para un puesto: **95 CV en 4 vacantes**: auxiliar de farmacia, cocinero, game designer y técnico de redes.",
"**94 de 95 se evaluaron** sin intervención; el que faltó era un **escaneo** y fue a revisión manual, como estaba previsto. Mediana de **13 s por CV**; todos dieron **JSON válido al primer intento** salvo 1.",
"Ojo: aquí **no hay etiquetas de referencia**, así que esto muestra **cobertura y estabilidad, no exactitud**. Los promedios bajos son normales: la mayoría de postulantes no cumple todo. En Farmacia, 6 evaluaciones tienen **correcciones de una persona**.",
]),
("Mejor que buscar palabras", "1:00", [
"¿Hace falta un LLM? Lo comparamos con lo que haría una persona con **Ctrl+F**: buscar las palabras clave de cada criterio.",
"La búsqueda acierta el **81,4 %** de los criterios con un **F1 de 0,59**; HireMind llega al **100 % con F1 1,00**. La diferencia está en lo que la búsqueda no entiende: **experiencia en un proyecto, una carrera en curso o contar años**.",
"A la derecha, la calidad del ranking: **0,96 en asistente contable y 1,00 en desarrollador junior**, ambas sobre la meta de 0,85. 1,00 significa que el top 5 sale en el mismo orden que el del reclutador.",
]),
("Equidad y robustez", "1:00", [
"Para la equidad tomamos **6 CV y creamos 4 variantes de cada uno**: sin datos personales, con edad y estado civil, con otra nacionalidad, y con un nombre del otro género. **Las 24 variantes dieron exactamente el mismo puntaje** que el original.",
"Además: el **CV escaneado fue a revisión manual**; en el **CV trampa**, un diseñador sin Python, **el agente no inventó Python**; **los 15 CV dieron el mismo puntaje en las 3 corridas**; y **no hubo citas inventadas**.",
"Sobre los datos personales: **el filtro limpió 8 de 9 CV**; en uno se le pasó un dato. **No cambió el puntaje**, porque esos datos nunca son criterio, pero lo dejamos anotado como mejora.",
"Un caso real: el aviso de **Farmareds pedía «edad entre 20 y 40 años»**. HireMind **rechaza ese criterio** porque es discriminatorio. Y las **preguntas de entrevista pasan por el mismo filtro**.",
]),
("La solución implementada", "1:30", [
"Esta es la aplicación real. **Panel** con procesos y distribución de puntajes; **vacante** con criterios y pesos que suman 100 %; **carga en lote** arrastrando los PDF; y el **ranking**, donde cada candidato tiene su **justificación y la cita del CV** que respalda cada criterio.",
"(Si hay tiempo: **demo en vivo** creando una vacante y subiendo 3 CV.)",
]),
("Del ranking a la entrevista", "1:00", [
"Lo nuevo: cuando la persona **elige a un candidato**, HireMind hace tres cosas. **Elige**: el reclutador lo marca desde el ranking. **Avisa**: arma un **correo** con el puesto y lo que destacó de su CV, con **vista previa** antes de enviar. **Prepara**: genera **6 a 8 preguntas** a partir de los criterios y la evidencia del CV, y pide verificar lo que salió parcial.",
"Las preguntas **no usan datos personales**; si LM Studio está apagado, se arman con una **plantilla por criterio**. En la demo el correo va en **modo prueba** a una cuenta del equipo.",
]),
("Limitaciones y futuro", "1:00", [
"Limitaciones: **solo lee PDF con texto**, los escaneados van a revisión manual; la rúbrica usa **palabras clave**, así que un sinónimo no previsto no cuenta; el modelo de **4B con 4 hilos ocupa unos 8 GB** entre RAM y swap, y un CV de 5 páginas tarda 49 s; la **exactitud se midió en 15 CV etiquetados**, los 95 del grupo no tienen etiquetas; el **correo va por Gmail**, con límite diario; y la app **aún no limita los cupos** de cada plan.",
"A futuro: en el **corto plazo**, OCR local con Tesseract y sinónimos con embeddings; a **mediano plazo**, modelos de 7 u 8B y los cupos de licencia; a **largo plazo**, un **piloto con 3 PYMEs** y la nube opcional para campañas masivas.",
]),
("Modelo de negocio híbrido", "1:00", [
"**Compra hoy, escala cuando crezcas.** La PYME compra una **licencia base perpetua de $299**, pago único: un equipo, **3 vacantes activas y 300 CV al año**, sin internet. Mientras su volumen sea bajo, **el costo mensual es $0**.",
"Si crece, activa una suscripción anual: **Plan Crecimiento, $149 al año** (12 vacantes, 1 500 CV, 3 equipos y modelo actualizado) o **Plan Escala, $299 al año** (sin límite local, 5 equipos, nube opcional y soporte prioritario).",
]),
("Esquema de ingresos", "0:45", [
"En el tiempo, para una PYME que crece en el año 2: **día 0**, licencia y setup, $374; **año 1**, un soporte puntual de $85; **años 2 y 3**, el Plan Crecimiento a $149 más una capacitación de $40.",
"**Un cliente así vale $797 en 3 años.** El ingreso fuerte entra al inicio y el recurrente llega solo si el cliente crece.",
]),
("Justificación de su pertinencia", "0:45", [
"Cinco pilares: **un solo pago** y sin tokens en la nube; **instalación asistida**; **menos de 15 s por CV**, para encontrar talento en un mercado con 52,8 % de informalidad; **100 % local**, que **cumple la LOPDP** y funciona sin internet estable; y **escalable** al crecer, sin reinstalar ni volver a aprender.",
]),
("Estructura tarifaria", "0:45", [
"Licencia base **$299**, **setup remoto obligatorio $75**, setup presencial opcional $120, **Crecimiento $149 al año**, **Escala $299 al año** y soporte puntual **$85**.",
"**El ticket de entrada es $299 + $75 = $374**, y se puede pagar con tarjeta diferida a 3 a 6 meses sin intereses o en dos partes del 50 %.",
]),
("Cálculo del precio", "1:30", [
"¿De dónde salen los números? Por cada cliente entran **$374**. Restamos el **setup, 3 horas a $10 = $30**; la **comisión de cobro del 6 %, $22**; y **una hora de garantía, $10**. Queda un **margen de contribución de $312 por cliente**.",
"Los **costos fijos del año** son: marketing digital $1 200, landing y dominio $120, contabilidad en RIMPE $360, depreciación del equipo de pruebas $300 y el **desarrollo, 480 horas a $6, amortizado en 3 años: $960**. En total, **$2 940**.",
"**$2 940 ÷ $312 = 9,4**, así que con **10 clientes al año cubrimos todos los costos**. Desde el cliente 11 hay ganancia, y las renovaciones de los años siguientes son casi margen puro.",
]),
("Valor para el cliente", "1:00", [
"Ahora desde el lado de la PYME, con **3 contrataciones al año durante 3 años**. Una **agencia** cobra alrededor del 75 % de un sueldo de $600 por proceso: **$4 050**. Los **portales de empleo**, a $60 por anuncio, **$540**, pero sin ningún filtrado.",
"**HireMind con Plan Crecimiento cuesta $672** en 3 años, y **solo con la licencia base, $374**.",
"**Frente a una agencia, la PYME ahorra $3 378**: la licencia se paga con **la primera contratación que no se terceriza**.",
]),
("Ingresos complementarios", "0:30", [
"Para los clientes sin suscripción quedan servicios puntuales: **reinstalación por nuevo hardware, $50 a $85**; **actualización de modelos, $60 a $100**; y **capacitación a nuevos usuarios, $40**.",
]),
("Análisis de riesgos", "1:00", [
"Ubicamos seis riesgos por probabilidad e impacto. El más serio es **R1, sesgo o error en el ranking**: lo mitigamos con reglas fijas, evidencia citada, el filtro de datos y **la decisión humana**.",
"**R2, equipos sin 16 GB**: auditoría de hardware en el setup. **R3, CV escaneados**: revisión manual y OCR en la hoja de ruta. **R4, fuga de datos**, con impacto alto pero baja probabilidad porque **todo es local**. **R5, modelo desactualizado**: actualización anual en los planes. **R6, baja adopción**: demo con CV reales del cliente y pago diferido.",
]),
("Sostenibilidad y mantenimiento", "1:00", [
"**Económica:** cada cliente deja $312 de margen desde el día 0 y el equilibrio está en unos **10 clientes al año**. **Técnica:** código abierto y modular; **cambiar de modelo es cambiar un nombre en la configuración**, y hay pruebas automáticas. **Ambiental y social:** usa el equipo que la PYME ya tiene, sin servidores con GPU, y **decide sin sesgo por edad, género o nacionalidad**.",
"Mantenimiento: **preventivo** cada año (modelo, respaldos, rúbricas), **correctivo** bajo demanda, **evolutivo** por versión (OCR, sinónimos) y **monitoreo continuo** del tiempo por CV y de las correcciones del reclutador.",
]),
("Conclusiones", "1:00", [
"Cuatro cifras resumen el proyecto: **100 % de criterios bien clasificados con un modelo de 4B** que corre en una laptop; **9,5 s por hoja de vida**, o sea 60 CV en menos de 10 minutos y sin internet; **24 de 24 variantes sin cambio de puntaje** al cambiar datos personales; y **$374 de entrada**, menos que una sola contratación por agencia.",
"La lección principal: **separar tareas funciona**. El LLM lee y redacta, Python puntúa con reglas fijas, **la persona elige** y el agente avisa y prepara la entrevista.",
]),
("Recomendaciones", "0:45", [
"**A las PYMEs:** definir criterios y pesos antes de abrir la vacante, revisar siempre el top 5 y pedir los CV en PDF digital.",
"**Al producto:** un piloto con 3 PYMEs y CV reales antes de vender, OCR y sinónimos, y **correo con dominio propio y agenda de entrevistas**. **Al negocio:** vender con una demo sobre los CV del propio cliente, ofrecer pago diferido y medir cuántos clientes pasan de la base al Plan Crecimiento.",
]),
("Referencias bibliográficas", "0:15", [
"Las fuentes de los datos del problema, de la métrica NDCG, del modelo Qwen3 y de los marcos de equidad y riesgo de IA (NIST AI RMF), más la LOPDP del Ecuador.",
]),
("¿Preguntas?", "0:15", [
"**Contrate con criterio: la IA ordena, usted decide.** Muchas gracias, quedamos atentos a sus preguntas.",
]),
]

FAQ = [
("¿Por qué 100 %? ¿No es sospechoso?", "Es sobre 15 CV ficticios armados y etiquetados por el equipo, con criterios claros. Demuestra que el diseño funciona, no que nunca falle: por eso la primera recomendación es un piloto con CV reales."),
("¿Por qué el modelo no pone la nota?", "Un modelo de 4B puede equivocarse o inventar. Las reglas en Python son explicables y auditables: el reclutador ve exactamente por qué cada CV tiene su puntaje."),
("¿Qué es la cita textual?", "La frase exacta del CV que respalda cada dato. Python la busca en el texto original; si no aparece, el dato vale 0 (\"no verificado\")."),
("¿Qué pasó con el dato personal que no se filtró?", "En 1 de 9 CV quedó un dato personal en el texto. No afecta el puntaje porque esos datos nunca son criterio (la prueba de equidad dio 24/24), pero está anotado como mejora."),
("¿Cómo se calculó el punto de equilibrio?", "Costos fijos de $2 940 al año divididos para un margen de $312 por cliente ($374 − $30 setup − $22 comisión − $10 garantía) = 9,4, o sea 10 clientes."),
("¿Por qué local y no en la nube?", "Privacidad (LOPDP), sin costos por uso y funciona sin internet estable. La nube es opcional y solo en el Plan Escala."),
("¿Por qué suscripción anual y no mensual?", "Las PYMEs contratan por temporadas: una mensualidad en meses sin vacantes se siente como gasto perdido y se cancela. Lo anual se presupuesta una vez y cuesta menos que doce cuotas."),
("¿Qué pasa si no renuevo?", "La licencia base es suya para siempre: vuelve al cupo base (3 vacantes activas, 300 CV al año) y puede pedir soporte puntual."),
("¿El correo le llega de verdad al candidato?", "En producción sí, por SMTP. Para la demo está en modo prueba: todos los correos se redirigen a una cuenta del equipo y el asunto indica a quién iban."),
("¿Por qué el promedio de Farmacia es tan bajo?", "Porque la mayoría de CV reales no cumple varios criterios del aviso, y 6 evaluaciones tienen correcciones humanas. En esos 95 CV no hay etiquetas, así que miden cobertura, no exactitud."),
("¿La IA decide a quién contratar?", "No. Ordena todos los CV con justificación; una persona revisa el top 5, corrige y decide a quién entrevistar."),
]


def md(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def thumb(i):
    b = (TH / f"s-{i:02d}.jpg").read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(b).decode()


def mins(t):
    m, s = t.split(":")
    return int(m) * 60 + int(s)


total = sum(mins(t) for _, t, _ in SL)
html = [f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Guion de exposición final · HireMind</title>
<style>
@page {{ size: A4; margin: 16mm; }}
:root {{ --navy:#0A0147; --mint:#2EE5A7; --coral:#FD696E; --blue:#5383FF; --ink:#1d1d2b; --muted:#5d6070; }}
* {{ box-sizing:border-box; }}
body {{ font-family: Montserrat, 'Open Sans', sans-serif; color:var(--ink); font-size:11pt; line-height:1.55; margin:0; background:#fff; }}
.cover {{ border-left:8px solid var(--mint); padding:4mm 0 4mm 7mm; margin-bottom:8mm; }}
.cover h1 {{ font-size:26pt; color:var(--navy); margin:0 0 2mm; font-weight:800; letter-spacing:-.5px; }}
.cover p {{ margin:0; color:var(--muted); font-size:10.5pt; }}
.tips {{ background:#F2F4FA; border-radius:8px; padding:4mm 6mm; font-size:10pt; margin-bottom:6mm; }}
.tips b {{ color:var(--navy); }}
.tips ul {{ margin:1mm 0 0; padding-left:5mm; }}
.slide {{ break-inside:avoid-page; margin:0 0 7mm; padding-top:5mm; border-top:1.5px solid #E3E5EE; }}
.hd {{ display:flex; gap:5mm; align-items:center; margin-bottom:3mm; }}
.hd img {{ width:46mm; border-radius:4px; box-shadow:0 0 0 1px #d8dbe6; flex:none; }}
.num {{ font-size:9pt; font-weight:700; color:var(--coral); letter-spacing:1px; text-transform:uppercase; }}
.hd h2 {{ font-size:15pt; margin:1mm 0 1.5mm; color:var(--navy); line-height:1.2; font-weight:800; }}
.time {{ display:inline-block; font-size:8.5pt; font-weight:700; background:var(--mint); color:var(--navy); border-radius:99px; padding:.5mm 3mm; }}
.slide p {{ margin:0 0 2.2mm; }}
.slide b {{ color:var(--navy); }}
.faq {{ break-before:page; }}
.faq h2 {{ color:var(--navy); font-size:16pt; margin:0 0 4mm; }}
.q {{ margin-bottom:4mm; break-inside:avoid; }}
.q b {{ color:var(--coral); }}
</style></head><body>
<div class="cover"><h1>HireMind · Guion de la exposición final</h1>
<p>Inteligencia Artificial · Grupo 5 &nbsp;·&nbsp; {len(SL)} diapositivas &nbsp;·&nbsp; duración aproximada {total//60} min {total%60:02d} s</p></div>
<div class="tips"><b>Cómo usar este guion</b><ul>
<li>Las <b>frases en negrita</b> son las ideas clave: si te pierdes, basta con decir esas.</li>
<li>No hace falta leerlo palabra por palabra; dilo con tus palabras señalando cada parte de la diapositiva.</li>
<li>Las cifras de evaluación salen de <b>hiremind/evaluacion/RESULTADOS.md</b>; si preguntan, ese es el respaldo.</li>
<li>Al final hay preguntas probables con su respuesta corta.</li></ul></div>
"""]
for i, (t, tm, ps) in enumerate(SL, 1):
    body = "".join(f"<p>{md(p)}</p>" for p in ps)
    html.append(f'<section class="slide"><div class="hd"><img src="{thumb(i)}" alt=""><div>'
                f'<div class="num">Diapositiva {i}</div><h2>{t}</h2><span class="time">≈ {tm} min</span></div></div>{body}</section>')
html.append('<section class="faq"><h2>Preguntas probables</h2>')
for q, a in FAQ:
    html.append(f'<div class="q"><b>{q}</b><br>{a}</div>')
html.append("</section></body></html>")
OUT.write_text("".join(html), encoding="utf-8")
print("diapositivas", len(SL), "total", total)
