"""Genera el guion de exposición (HTML) con miniaturas de cada diapositiva."""
import base64, pathlib, re, sys

S = pathlib.Path(__file__).parent
OUT = pathlib.Path(sys.argv[1])

# (título, minutos, [párrafos]); **negrita** marca las frases clave
SL = [
("HireMind", "0:30", [
"Buenos días. Somos el grupo 5 y les presentamos **HireMind**, un agente de inteligencia artificial que ayuda a las **PYMEs ecuatorianas** a preseleccionar hojas de vida.",
"La idea es simple: cuando una pequeña empresa recibe decenas de CV para una vacante, el agente los lee, los compara con lo que la empresa necesita y entrega un **ranking justificado**. Todo corre **en el propio computador de la empresa** y **la decisión final siempre la toma una persona**.",
"Primero les contamos el problema, luego cómo funciona el agente por dentro y al final el modelo de negocio.",
]),
("Muchos postulantes y talento difícil de hallar", "1:00", [
"Empecemos por el contexto. Ecuador tiene una **tasa de desempleo del 3,1 %** en 2026, pero el número engaña: el **52,8 % de los desempleados ha tenido empleos informales** y el **36 % no tiene experiencia** formal (Primicias).",
"¿Qué significa esto para quien contrata? Que llegan **muchos postulantes con perfiles muy distintos**, y que el talento no siempre se ve a simple vista en un CV.",
"Además, el **54 % de los expertos en recursos humanos busca habilidades blandas** (El Diario, 2025), que son justamente las más difíciles de detectar leyendo hojas de vida a la rápida.",
]),
("Contratar con poco tiempo y sin criterio sale caro", "1:00", [
"Aterricemos el problema en cuatro puntos.",
"**Afectado:** las PYMEs ecuatorianas, sobre todo las que **no tienen un departamento de recursos humanos**. Ahí normalmente contrata el dueño o el administrador.",
"**Problema concreto:** las hojas de vida se **revisan a mano**, **sin criterios consistentes**, con poco tiempo y sin margen para equivocarse.",
"**Situación:** llegan muchos postulantes con perfiles heterogéneos, y las habilidades blandas son difíciles de encontrar.",
"**Consecuencias:** procesos lentos, decisiones inconsistentes, **riesgo de una mala contratación** y tiempo que se le quita a la operación del negocio. Para una empresa pequeña, una mala contratación sale cara.",
]),
("Arquitectura completa del agente", "2:00", [
"Ahora veamos cómo está construido el agente. Lo primero es este recuadro grande: **todo el sistema corre en el equipo local de la PYME**, con unos 16 GB de RAM. **Los CV nunca salen a internet**, y eso importa porque son datos personales.",
"A la izquierda está el **reclutador**: define los criterios de la vacante, sube los CV y toma la decisión final. Él trabaja en una **interfaz en Streamlit** con tres pantallas: registrar la vacante, cargar las hojas de vida en PDF y ver el ranking.",
"Debajo está el **núcleo del agente en Python**, que coordina todo con seis componentes: la **ingesta** de PDF con PyMuPDF; el **cliente LLM**, que le pide al modelo una respuesta en JSON; el **validador**, que revisa ese JSON; el **verificador de evidencia**, que comprueba que cada dato tenga una cita real en el CV; el **filtro de equidad**, que ignora foto, género, edad, nacionalidad y religión; y el **motor de puntuación**.",
"A la derecha está el modelo, **Qwen 2.5 de 4B**, corriendo en **LM Studio** como servidor local. La idea clave del diseño: **el modelo solo extrae datos y redacta la justificación, no pone la nota**. La nota la calcula Python con reglas claras.",
"Todo se guarda en **SQLite**, una base de datos local. Y si una empresa necesita más capacidad, se puede **escalar a un modelo de 7B o a Gemini en la nube** sin cambiar el resto.",
]),
("Flujo de razonamiento del agente", "2:00", [
"Esta diapositiva muestra cómo \"piensa\" el agente con cada hoja de vida. Las franjas indican quién hace qué: **el LLM extrae y redacta, Python valida y puntúa, y la persona decide**.",
"**Paso 1:** se lee el PDF. Si el texto no es legible, por ejemplo un PDF escaneado, el CV **no se descarta: pasa a revisión manual**.",
"**Paso 2:** el modelo convierte el CV a JSON: formación, experiencia, habilidades y proyectos. Y por cada dato **copia la frase exacta del CV que lo respalda**, la cita textual.",
"**Paso 3:** se valida el JSON. Si sale mal, se reintenta con el error, máximo dos veces; si sigue fallando, va a revisión manual.",
"**Paso 4:** se verifica la evidencia. Si una cita no existe en el CV, ese dato queda como **\"no verificado\" y vale cero**. Así el modelo no puede inventar.",
"**Paso 5:** se excluyen los datos personales sensibles. **Paso 6:** Python compara con los criterios —cumple, parcial o no identificado— y calcula el puntaje con las ponderaciones del reclutador. **Paso 7:** el modelo redacta la justificación solo con evidencias verificadas. **Paso 8:** se guarda el resultado.",
"Y lo más importante: **la IA no contrata ni descarta a nadie**. Ordena los CV, y **una persona revisa el top 5** y decide a quién entrevistar.",
]),
("Criterios de selección del LLM y alternativas de escalamiento", "1:30", [
"¿Por qué elegimos **Qwen 2.5 de 4B**? Usamos siete criterios: **comprensión del español**, porque los CV y las vacantes están en español; **extracción de información**; **salida en JSON** para que Python procese los datos; capacidad de **comparar y dar evidencia**; **velocidad en local**; una **API compatible con OpenAI** para integrarlo fácil; y **100 % de privacidad local**.",
"En el centro está el dimensionamiento de memoria en un equipo de **16 GB**: el modelo ocupa entre **1,8 y 2,5 GB**, la ventana de contexto entre **0,8 y 1,5 GB**, y quedan libres **entre 12 y 13,5 GB** para el sistema y Streamlit. O sea, **funciona en un computador de oficina normal**.",
"Y si hace falta más: localmente se puede subir a **Qwen 7B o Mistral 7B** para más razonamiento, o pasar a **Gemini Flash en la nube** si la empresa necesita procesar volúmenes masivos.",
]),
("Herramientas seleccionadas y su rol en la arquitectura", "1:00", [
"Estas son las herramientas, con **Python en el centro** coordinando todo y calculando los puntajes.",
"**Streamlit** es la interfaz web, hecha directamente en Python, sin un frontend aparte. **PyMuPDF** extrae el texto de los PDF. **SQLite** es la base de datos local, que no necesita servidor. **LM Studio** ejecuta el modelo y expone una API local. El **SDK de OpenAI** es el cliente con el que Python le habla a esa API. Y **VS Code** es el editor del código.",
"El criterio general fue **reducir complejidad**: bibliotecas conocidas, gratuitas y **sin servidores ni servicios innecesarios**, para que se pueda instalar en cualquier PYME.",
]),
("Flujo de trabajo paso a paso y evaluación responsable", "1:30", [
"Así se ve el proceso desde el lado del usuario, en siete pasos: **1)** se inicia LM Studio con Qwen 4B; **2)** se configura la vacante en Streamlit; **3)** se cargan los CV en PDF; **4)** PyMuPDF extrae el texto; **5)** el modelo devuelve el JSON por la API local; **6)** Python calcula los puntajes; y **7)** se guarda en SQLite y se muestra el ranking.",
"Abajo están los cuatro **principios de evaluación responsable**: **sin sesgos personales**, porque no se usan foto, género, edad ni nacionalidad; **evidencia verificable**, porque todo puntaje tiene su cita en el CV; **decisión final humana**, porque el ranking es solo apoyo; y **privacidad y control de datos**, porque todo queda en el equipo de la empresa.",
]),
("Métricas y protocolo de evaluación", "1:30", [
"¿Cómo sabremos si el agente funciona? Definimos seis métricas con metas concretas:",
"**Tasa de éxito ≥ 95 %** de evaluaciones completadas. **Precisión de extracción, F1 ≥ 90 %** en formación, experiencia y habilidades. **Calidad del ranking, NDCG@5 ≥ 0,85** comparado con la evaluación de una persona. **Tiempo de respuesta ≤ 15 s por CV** en promedio, con P95 ≤ 30 s. **100 % de JSON válidos** y al menos 95 % de resultados justificados. Y **confiabilidad y equidad ≥ 99 %**: sin sesgos y disponible.",
"El protocolo tiene seis pasos: **preparar un conjunto de CV** diversos con una referencia manual; **probar la extracción** midiendo precisión, recall y F1; **probar la clasificación** contra evaluadores humanos con NDCG@5; medir **rendimiento** con 1, 10, 25 y 50 documentos, viendo RAM y latencia; revisar **consistencia y equidad**; y finalmente **analizar los resultados** en una tabla comparativa.",
]),
("Modelo de negocio híbrido: base perpetua + expansiones anuales", "1:00", [
"Pasamos al negocio. HireMind usa un **modelo híbrido**: la PYME **compra el programa base una sola vez** y, **cuando crece**, amplía su capacidad con una **suscripción anual**.",
"La propuesta de valor: una herramienta **privada y de pago único** que resuelve la contratación base **sin atar a la empresa a cuotas mensuales desde el inicio**, pero que **crece al mismo ritmo del negocio**.",
"Tiene cuatro componentes: la **licencia base perpetua**, con un cupo para contrataciones moderadas; el **setup inicial**, con verificación del equipo de 16 GB, LM Studio, el modelo Qwen 4B y capacitación; las **expansiones anuales**, que suben el límite de vacantes y de CV, suman equipos y modelos más grandes; y el **soporte puntual bajo demanda** para quien se queda solo con la base.",
"Nuestros clientes son **dueños y administradores de PYMEs sin departamento de talento humano** que contratan por temporadas, y **PYMEs en expansión** que reclutan cada vez más.",
]),
("Esquema de ingresos", "0:45", [
"En el tiempo: **un pago único al inicio** —licencia base más setup— y mientras el volumen sea bajo, **el costo mensual es cero**.",
"Cuando la empresa **llega al tope** de vacantes o de CV, activa una **expansión anual**. ¿Por qué **anual y no mensual**? Tres razones: el crecimiento de una PYME **se consolida año a año**, no de un mes a otro; **no se paga en los meses sin vacantes**, que es lo que hace cancelar una mensualidad; y es **un solo presupuesto al año**, más barato que doce cuotas.",
]),
("Justificación de su pertinencia", "1:00", [
"¿Por qué tiene sentido para las PYMEs ecuatorianas? Por cinco pilares:",
"**Adaptación financiera:** respeta la idea de **\"comprarlo y que sea mío\"**; la suscripción solo llega cuando el crecimiento la justifica, con **$0 en tokens** en la etapa base. **Cero barreras técnicas:** instalación asistida e interfaz web simple; al expandirse, **no hay que reinstalar ni aprender de nuevo**. **Mercado laboral: menos de 15 segundos por CV**, para encontrar talento sin historial tradicional en un país con **52,8 % de informalidad**. **Privacidad: 100 % local**, funciona con internet inestable y **cumple la Ley Orgánica de Protección de Datos Personales**. Y **escalabilidad progresiva:** de un solo computador a modelos de 7 u 8 mil millones de parámetros, o a la nube si el volumen se vuelve masivo.",
]),
("Estructura tarifaria", "1:00", [
"Los precios. La **Licencia Base Perpetua cuesta $299**, pago único: un equipo, **hasta 3 vacantes activas y 60 CV por vacante, máximo 300 CV al año**, sin tokens y sin internet.",
"El **setup remoto, $75, es obligatorio**: auditoría del hardware, instalación remota y 45 minutos de capacitación. El **setup presencial, $120, es opcional**. Entonces, **el ticket de entrada es $374, una sola vez**.",
"Para crecer hay dos expansiones anuales: el **Plan Crecimiento, $149 al año**, con **12 vacantes y 1 500 CV al año**, hasta **3 equipos** y la actualización anual del modelo; y el **Plan Escala, $299 al año**, **sin límite local**, hasta **5 equipos**, respaldo automático y la opción de **procesar en la nube** campañas masivas. Quien se queda con la base tiene **soporte puntual a $85**.",
"¿Se justifica? Una **agencia cobra entre $230 y $500 por una sola contratación**: aun sumando el Plan Crecimiento, el año completo cuesta menos que un proceso tercerizado. Y frente a **portales de $40 a $80 por anuncio**, con unas 3 contrataciones al año **la licencia se paga en 18 meses**.",
]),
("Ingresos complementarios", "0:45", [
"Por último, el modelo arma una **escalera de ingresos**. La principal: cuando la PYME **llega al tope** de su licencia base, la propia aplicación le avisa que puede **ampliar con el Plan Crecimiento o Escala**: así un cliente de un solo pago se vuelve **ingreso anual recurrente sin venta agresiva**.",
"Para quien no tiene suscripción quedan los servicios puntuales: **reinstalación por nuevo hardware, $50 a $85**; **actualización de modelos de IA, $60 a $100**; y **capacitación a nuevos usuarios, $40**.",
"**Para cerrar:** HireMind le da a una PYME sin departamento de recursos humanos una forma **rápida, justa y privada** de ordenar sus postulantes, con **evidencia en cada puntaje**. **Compra hoy, escala cuando crezcas**, y **la decisión siempre en manos de una persona**. Muchas gracias, quedamos atentos a sus preguntas.",
]),
]

FAQ = [
("¿Por qué el modelo no pone la nota?", "Un modelo de 4B puede equivocarse o inventar. Las reglas en Python son explicables y auditables: el reclutador ve exactamente por qué cada CV tiene su puntaje."),
("¿Qué es la cita textual?", "El fragmento exacto del CV que respalda cada dato extraído. Python lo busca en el texto original; si no aparece, el dato vale 0 (\"no verificado\")."),
("¿Qué pasa con un PDF escaneado?", "No se descarta: va a revisión manual. El agente nunca elimina un CV por no poder leerlo."),
("¿Por qué local y no en la nube?", "Privacidad (LOPDP), sin costos por uso y funciona sin internet estable. La nube es opcional y solo en el Plan Escala, para campañas masivas."),
("¿Por qué suscripción anual y no mensual?", "Las PYMEs contratan por temporadas: una mensualidad en meses sin vacantes se siente como gasto perdido y se cancela. El pago anual cubre los picos, se presupuesta una vez y cuesta menos que doce cuotas."),
("¿Qué pasa si no renuevo la expansión?", "La licencia base sigue siendo suya para siempre: vuelve al cupo base (3 vacantes activas, 300 CV al año) y puede pedir soporte puntual."),
("¿La IA decide a quién contratar?", "No. Ordena todos los CV con justificación; una persona revisa el top 5, corrige errores y decide a quién entrevistar."),
]


def md(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def thumb(i):
    b = (S / "th" / f"s-{i:02d}.jpg").read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(b).decode()


def mins(t):
    m, s = t.split(":")
    return int(m) * 60 + int(s)


total = sum(mins(t) for _, t, _ in SL)
html = [f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Guion de exposición · HireMind</title>
<style>
@page {{ size: A4; margin: 16mm 16mm 16mm 16mm; }}
:root {{ --navy:#0A0147; --mint:#2EE5A7; --coral:#FD696E; --blue:#5383FF; --ink:#1d1d2b; --muted:#5d6070; }}
* {{ box-sizing:border-box; }}
body {{ font-family: Montserrat, 'Open Sans', sans-serif; color:var(--ink); font-size:11.3pt; line-height:1.55; margin:0; background:#fff; }}
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
<div class="cover"><h1>HireMind · Guion de exposición</h1>
<p>Entregable 1 · Inteligencia Artificial · Grupo 5 &nbsp;·&nbsp; 14 diapositivas &nbsp;·&nbsp; duración aproximada {total//60} min {total%60:02d} s</p></div>
<div class="tips"><b>Cómo usar este guion</b><ul>
<li>Las <b>frases en negrita</b> son las ideas clave: si te pierdes, basta con decir esas.</li>
<li>No hace falta leerlo palabra por palabra; dilo con tus propias palabras señalando cada parte de la diapositiva.</li>
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
print("total", total)
