"""Genera hojas de vida FICTICIAS en PDF para probar el agente.

Todas las personas, empresas y datos son inventados.
Incluye casos especiales:
  - cv_08_escaneado.pdf: PDF de solo imagen -> debe ir a revisión manual
  - cv_13_trampa_disenador.pdf: perfil sin programación -> el agente no debe inventar Python
  - varios CV traen edad, estado civil o nacionalidad -> el filtro de equidad debe quitarlos

Uso:  python scripts/generar_cvs.py [carpeta_salida]
"""
from __future__ import annotations

import sys
from pathlib import Path

import pymupdf

CSS = """
* { font-family: sans-serif; }
h1 { font-size: 17pt; margin: 0 0 2pt 0; }
h2 { font-size: 11.5pt; margin: 10pt 0 3pt 0; border-bottom: 1px solid #444; }
p, li { font-size: 9.8pt; margin: 1pt 0; }
.sub { font-size: 10pt; color: #333; }
"""

# (archivo, nombre, titular, datos_personales, secciones)  — secciones: [(título, [líneas])]
CVS = [
    ("cv_01_contable.pdf", "Andrea Salazar Vinueza", "Ingeniera en Contabilidad y Auditoría · CPA",
     ["Fecha de nacimiento: 14/05/1996", "Estado civil: Soltera", "Teléfono: 099 000 0001"],
     [("Perfil", ["Contadora con experiencia en PYMEs comerciales, orientada al cumplimiento tributario y a la atención al cliente."]),
      ("Formación académica", ["Ingeniería en Contabilidad y Auditoría CPA, Universidad Central del Ecuador (2014-2019)."]),
      ("Experiencia laboral", [
          "Asistente contable, Comercial Los Andes (2021-02 a la actualidad): registro de compras y ventas, facturación electrónica, declaraciones mensuales de IVA y ATS en el SRI.",
          "Auxiliar contable, Distribuidora Pichincha (2019-08 a 2021-01): conciliaciones bancarias y retenciones."]),
      ("Habilidades", ["Excel avanzado (tablas dinámicas, BUSCARV)", "Facturación electrónica SRI", "Atención al cliente", "Sistema contable Mónica"]),
      ("Idiomas", ["Inglés: nivel básico (A2)."])]),
    ("cv_02_contable.pdf", "Carlos Ortiz Guamán", "Licenciado en Contabilidad",
     ["Nacionalidad: Ecuatoriana", "Edad: 31 años"],
     [("Formación académica", ["Licenciatura en Contabilidad, Universidad Politécnica Salesiana (2012-2017)."]),
      ("Experiencia laboral", [
          "Auxiliar contable, Ferretería San Blas (2022-01 a 2024-06): ingreso de facturas, cálculo de retenciones y reportes en Excel.",
          "Bodeguero, Almacenes Tía (2018-03 a 2021-10): control de inventario."]),
      ("Habilidades", ["Microsoft Excel intermedio", "Retenciones en la fuente", "Trabajo en equipo"])]),
    ("cv_03_contable.pdf", "María José Paredes León", "Tecnóloga en Contabilidad",
     ["Estado civil: Casada"],
     [("Formación académica", ["Tecnología Superior en Contabilidad, Instituto Tecnológico Quito (2015-2018)."]),
      ("Experiencia laboral", [
          "Contadora, Tienda de electrodomésticos Mi Hogar (2022-09 a la actualidad): contabilidad completa, facturación electrónica y declaraciones en el SRI.",
          "Cajera y servicio al cliente, Supermercado La Favorita (2019-01 a 2022-08)."]),
      ("Habilidades", ["Excel (tablas dinámicas)", "Declaraciones SRI", "Servicio al cliente"])]),
    ("cv_04_contable.pdf", "Luis Andrango Cusco", "Ingeniero Comercial",
     [],
     [("Formación académica", ["Ingeniería Comercial, Pontificia Universidad Católica del Ecuador (2013-2018)."]),
      ("Experiencia laboral", [
          "Asistente contable, Importadora del Sur (2025-05 a la actualidad): registro de facturas de proveedores.",
          "Vendedor, Tecnicentro Norte (2019-01 a 2025-04): atención al cliente y cierre de caja."]),
      ("Habilidades", ["Excel", "Atención al cliente", "Negociación"])]),
    ("cv_05_contable.pdf", "Gabriela Yánez Ruiz", "Estudiante de Contabilidad",
     ["Fecha de nacimiento: 02/11/2004"],
     [("Formación académica", ["Cursando sexto semestre de Contabilidad y Auditoría, Universidad Central del Ecuador.",
                               "Bachillerato en Contabilidad, Colegio Montúfar (2022)."]),
      ("Experiencia laboral", ["Prácticas preprofesionales contables, Estudio Contable Ruiz & Asociados (2025-03 a 2025-09): archivo y digitación de comprobantes."]),
      ("Habilidades", ["Excel", "Organización"])]),
    ("cv_06_contable.pdf", "Jorge Cevallos Mena", "Bachiller",
     ["Estado civil: Soltero", "Nacionalidad: Ecuatoriana"],
     [("Formación académica", ["Bachillerato General Unificado, Colegio Nacional Benalcázar (2016)."]),
      ("Experiencia laboral", ["Cajero, Farmacias Cruz Azul (2021-02 a la actualidad): atención al cliente y manejo de caja."]),
      ("Habilidades", ["Atención al cliente", "Excel básico"])]),
    ("cv_07_contable.pdf", "Daniela Mora Castillo", "Magíster en Finanzas · CPA",
     [],
     [("Formación académica", ["Maestría en Finanzas, Universidad Andina Simón Bolívar (2020-2022).",
                               "Ingeniería en Contabilidad y Auditoría CPA, Escuela Politécnica del Ejército (2011-2016)."]),
      ("Experiencia laboral", ["Contadora general, Grupo Constructor Sierra (2017-01 a la actualidad): estados financieros, declaraciones y anexos en el SRI, facturación electrónica, supervisión de dos auxiliares."]),
      ("Habilidades", ["Excel avanzado y Power BI", "Anexos transaccionales (ATS)", "Liderazgo"]),
      ("Idiomas", ["Inglés intermedio (B1)."])]),
    ("cv_08_escaneado.pdf", "Paúl Vega Toapanta", "Contador",
     [],
     [("Formación académica", ["Licenciatura en Contabilidad, Universidad de Guayaquil (2010-2015)."]),
      ("Experiencia laboral", ["Contador, Ferretería Ochoa (2016-01 a la actualidad)."]),
      ("Habilidades", ["Excel", "SRI"])]),
    ("cv_09_dev.pdf", "Sebastián Torres Almeida", "Ingeniero de Software",
     ["Fecha de nacimiento: 21/08/1999"],
     [("Formación académica", ["Ingeniería de Software, Escuela Politécnica Nacional (2017-2022)."]),
      ("Experiencia laboral", ["Desarrollador backend, Fintech Kapital (2024-01 a la actualidad): APIs en Python con Django y PostgreSQL, pruebas automatizadas."]),
      ("Habilidades", ["Python", "Django", "PostgreSQL", "Git"]),
      ("Idiomas", ["Inglés intermedio-alto (B2)."])]),
    ("cv_10_dev.pdf", "Valeria Chicaiza Pilco", "Tecnóloga en Desarrollo de Software",
     [],
     [("Formación académica", ["Tecnología Superior en Desarrollo de Software, Instituto Tecnológico Sucre (2019-2022)."]),
      ("Experiencia laboral", ["Programadora web, Agencia Digital Mitad del Mundo (2024-03 a la actualidad): sitios en PHP con Laravel y MySQL."]),
      ("Proyectos", ["Bot de inventario: script en Python que lee hojas de Excel y envía alertas de stock."]),
      ("Habilidades", ["PHP", "Laravel", "MySQL", "HTML y CSS"]),
      ("Idiomas", ["Inglés básico (A2)."])]),
    ("cv_11_dev.pdf", "Diego Lema Quishpe", "Estudiante de Ingeniería en Sistemas",
     ["Edad: 22 años", "Estado civil: Soltero"],
     [("Formación académica", ["Cursando octavo semestre de Ingeniería en Sistemas, Escuela Politécnica Nacional."]),
      ("Proyectos", ["Sistema de turnos para un consultorio con Python, Flask y SQLite (proyecto de clase).",
                     "Web scraper de precios de supermercados en Python."]),
      ("Habilidades", ["Python", "Flask", "Git"]),
      ("Idiomas", ["Inglés intermedio (B1), certificado por el Centro de Educación Continua."])]),
    ("cv_12_dev.pdf", "Karla Benítez Ordóñez", "Ingeniera en Sistemas",
     ["Nacionalidad: Colombiana"],
     [("Formación académica", ["Ingeniería en Sistemas Informáticos, Universidad de las Fuerzas Armadas ESPE (2014-2019)."]),
      ("Experiencia laboral", ["Desarrolladora full stack, Logística Express (2021-06 a la actualidad): servicios con Python y FastAPI, base de datos SQL Server y frontend en React.",
                               "Programadora junior, Soluciones TIC (2019-10 a 2021-05): mantenimiento de sistemas en Java."]),
      ("Habilidades", ["Python", "FastAPI", "SQL Server", "React", "Docker"]),
      ("Idiomas", ["Inglés avanzado (C1)."])]),
    ("cv_13_trampa_disenador.pdf", "Andrés Pozo Viteri", "Diseñador Gráfico",
     [],
     [("Formación académica", ["Licenciatura en Diseño Gráfico, Universidad San Francisco de Quito (2015-2019)."]),
      ("Experiencia laboral", ["Diseñador gráfico, Estudio Creativo Pixel (2020-01 a la actualidad): identidad visual, redes sociales y material impreso."]),
      ("Habilidades", ["Adobe Photoshop", "Adobe Illustrator", "Figma", "Fotografía de producto"]),
      ("Intereses", ["Me interesa aprender a programar en el futuro."])]),
    ("cv_14_dev.pdf", "Fernanda Ruiz Saltos", "Ingeniera Electrónica",
     [],
     [("Formación académica", ["Ingeniería en Electrónica y Control, Escuela Politécnica Nacional (2015-2021)."]),
      ("Experiencia laboral", ["Programadora de automatización, Industrias Lácteas Andinas (2025-01 a la actualidad): scripts en Python para leer sensores de planta y guardar datos en MySQL."]),
      ("Habilidades", ["Python", "MySQL", "PLC Siemens"]),
      ("Idiomas", ["Inglés intermedio (B2)."])]),
    ("cv_15_dev.pdf", "Mateo Herrera Jácome", "Asistente administrativo",
     ["Estado civil: Casado"],
     [("Formación académica", ["Bachillerato en Informática, Unidad Educativa Juan Pío Montúfar (2018).",
                               "Curso de Python básico (40 horas), Fundación Código Ecuador (2024)."]),
      ("Experiencia laboral", ["Asistente administrativo, Notaría Quinta de Quito (2020-05 a la actualidad): archivo, agenda y atención al público."]),
      ("Habilidades", ["Microsoft Office", "Atención al público"])]),
]


def html_cv(nombre, titular, personales, secciones) -> str:
    h = [f"<h1>{nombre}</h1><p class='sub'>{titular}</p>"]
    h += [f"<p>{d}</p>" for d in personales]
    h.append("<p>Correo: (dato ficticio) · Quito, Ecuador</p>")
    for titulo, lineas in secciones:
        h.append(f"<h2>{titulo}</h2><ul>" + "".join(f"<li>{l}</li>" for l in lineas) + "</ul>")
    return "".join(h)


def crear_pdf(html: str) -> pymupdf.Document:
    doc = pymupdf.open()
    pagina = doc.new_page(width=595, height=842)  # A4
    pagina.insert_htmlbox(pymupdf.Rect(50, 50, 545, 800), html, css=CSS)
    return doc


def escanear(doc: pymupdf.Document) -> pymupdf.Document:
    """Simula un CV escaneado: la página queda como imagen, sin texto extraíble."""
    pix = doc[0].get_pixmap(dpi=110, colorspace=pymupdf.csGRAY)
    nuevo = pymupdf.open()
    p = nuevo.new_page(width=595, height=842)
    p.insert_image(p.rect, pixmap=pix)
    return nuevo


def main(salida: Path) -> None:
    salida.mkdir(parents=True, exist_ok=True)
    for archivo, nombre, titular, personales, secciones in CVS:
        doc = crear_pdf(html_cv(nombre, titular, personales, secciones))
        if "escaneado" in archivo:
            doc = escanear(doc)
        doc.save(salida / archivo, garbage=3, deflate=True)
        print("ok", archivo)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "datos" / "cvs")
