"""Vacantes de ejemplo para probar el agente."""
from .modelos import Criterio, Vacante

VACANTES_DEMO = [
    Vacante(
        titulo="Asistente contable · Ferretería El Constructor (Quito)",
        descripcion="Registro de compras y ventas, facturación electrónica, conciliaciones y apoyo en declaraciones al SRI.",
        criterios=[
            Criterio(id="form", tipo="formacion", nombre="Formación en contabilidad (tercer nivel)", peso=25,
                     nivel_min="tercer_nivel", palabras_clave=["contabilidad", "contable", "auditoria", "cpa", "finanzas"]),
            Criterio(id="exp", tipo="experiencia", nombre="Experiencia contable (2 años)", peso=30, anios_min=2,
                     palabras_clave=["contable", "contabilidad", "contador", "contadora", "auxiliar contable", "asistente contable"]),
            Criterio(id="excel", tipo="habilidad", nombre="Excel", peso=20,
                     palabras_clave=["excel", "hojas de calculo", "tablas dinamicas", "buscarv"]),
            Criterio(id="sri", tipo="habilidad", nombre="Facturación electrónica / SRI", peso=15,
                     palabras_clave=["facturacion electronica", "sri", "declaraciones", "ats", "retenciones"]),
            Criterio(id="cliente", tipo="habilidad", nombre="Atención al cliente", peso=10,
                     palabras_clave=["atencion al cliente", "servicio al cliente", "atencion a clientes"]),
        ],
    ),
    Vacante(
        titulo="Desarrollador/a junior Python · Software Andino (Quito)",
        descripcion="Mantenimiento de una aplicación web interna y automatización de reportes.",
        criterios=[
            Criterio(id="py", tipo="habilidad", nombre="Python", peso=30, palabras_clave=["python", "django", "flask", "fastapi"]),
            Criterio(id="exp", tipo="experiencia", nombre="Experiencia en desarrollo (1 año)", peso=25, anios_min=1,
                     palabras_clave=["desarrollador", "desarrolladora", "programador", "programadora", "developer",
                                     "desarrollo de software", "backend", "full stack"]),
            Criterio(id="form", tipo="formacion", nombre="Formación en sistemas o software (tecnólogo)", peso=20,
                     nivel_min="tecnologo", palabras_clave=["sistemas", "software", "computacion", "informatica", "desarrollo de software"]),
            Criterio(id="sql", tipo="habilidad", nombre="Bases de datos SQL", peso=15,
                     palabras_clave=["sql", "postgresql", "mysql", "sqlite", "sql server"]),
            Criterio(id="en", tipo="idioma", nombre="Inglés intermedio", peso=10, idioma="ingles",
                     nivel_idioma="intermedio", palabras_clave=["english"]),
        ],
    ),
]
