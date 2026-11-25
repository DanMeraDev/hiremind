"""Vacantes de los CV de prueba que aportó cada integrante (datos/seeds/<carpeta>/).

Farmareds trae su aviso real (datos/seeds/farmareds/vacante.pdf). Las demás no tenían
aviso: los criterios se definieron a partir del perfil que buscan los CV.
"""
from pathlib import Path

from .modelos import Criterio as C, Vacante

CARPETA = Path(__file__).resolve().parent.parent / "datos" / "seeds"

VACANTES_SEEDS: dict[str, Vacante] = {
    # El aviso pide "Edad entre 20 y 40 años": ese requisito NO se incluye (HireMind lo rechaza por discriminatorio).
    "farmareds": Vacante(
        titulo="Auxiliar de farmacia · Farmareds",
        descripcion="Atender y asesorar clientes, despachar recetas, facturar, cuadrar caja y controlar inventario "
                    "y caducidades. Tiempo completo, turnos rotativos.",
        criterios=[
            C(id="exp", tipo="experiencia", nombre="Experiencia en farmacia, mostrador o ventas (1 año)", peso=30,
              anios_min=1, palabras_clave=["farmacia", "farmaceutico", "farmaceutica", "botica", "mostrador", "ventas",
                                           "vendedor", "vendedora", "dependiente", "cajero", "cajera", "atencion al cliente"]),
            C(id="form", tipo="formacion", nombre="Bachiller o técnico en farmacia", peso=15, nivel_min="bachillerato"),
            C(id="med", tipo="habilidad", nombre="Conocimiento de medicamentos", peso=20,
              palabras_clave=["medicamentos", "farmacologia", "farmacia", "recetas", "dispensacion", "despacho de recetas",
                              "inyectologia", "principios activos"]),
            C(id="caja", tipo="habilidad", nombre="Caja y facturación electrónica", peso=15,
              palabras_clave=["caja", "facturacion", "facturacion electronica", "cobro", "cuadre de caja", "punto de venta"]),
            C(id="inv", tipo="habilidad", nombre="Inventario y control de caducidad", peso=10,
              palabras_clave=["inventario", "kardex", "caducidad", "vencimiento", "bodega", "stock", "mercaderia"]),
            C(id="cli", tipo="habilidad", nombre="Atención al cliente", peso=10,
              palabras_clave=["atencion al cliente", "servicio al cliente", "asesoria", "atencion a clientes"]),
        ],
    ),
    "cocinero": Vacante(
        titulo="Cocinero/a · Restaurante de comida ecuatoriana (Quito)",
        descripcion="Cocina caliente y producción diaria de menú y carta, mise en place, control de inventario y "
                    "cumplimiento de normas de higiene.",
        criterios=[
            C(id="exp", tipo="experiencia", nombre="Experiencia en cocina (2 años)", peso=30, anios_min=2,
              palabras_clave=["cocinero", "cocinera", "cocina", "chef", "sous chef", "ayudante de cocina",
                              "jefe de partida", "auxiliar de cocina", "parrillero"]),
            C(id="cal", tipo="habilidad", nombre="Cocina caliente y ecuatoriana", peso=20,
              palabras_clave=["cocina caliente", "cocina ecuatoriana", "parrilla", "salteado", "fritura", "platos tipicos"]),
            C(id="bpm", tipo="habilidad", nombre="Higiene e inocuidad (BPM / HACCP)", peso=20,
              palabras_clave=["bpm", "haccp", "manipulacion de alimentos", "inocuidad", "buenas practicas de manufactura"]),
            C(id="form", tipo="formacion", nombre="Formación en gastronomía (técnico)", peso=15, nivel_min="tecnico",
              palabras_clave=["gastronomia", "cocina", "arte culinario", "chef", "culinaria"]),
            C(id="cost", tipo="habilidad", nombre="Costos, inventario y fichas técnicas", peso=15,
              palabras_clave=["costos", "costeo", "fichas tecnicas", "inventario", "fifo", "food cost", "compras"]),
        ],
    ),
    "game_designer": Vacante(
        titulo="Game designer junior · Estudio de videojuegos",
        descripcion="Diseñar mecánicas y sistemas, prototipar, balancear y documentar (GDD) junto al equipo de desarrollo.",
        criterios=[
            C(id="dis", tipo="habilidad", nombre="Diseño de mecánicas y sistemas", peso=25,
              palabras_clave=["diseno de sistemas", "mecanicas", "diseno de niveles", "diseno de reglas", "game design",
                              "balance", "economia de recursos", "loop de juego"]),
            C(id="motor", tipo="habilidad", nombre="Motor de videojuegos (Unity / Godot / Unreal)", peso=20,
              palabras_clave=["unity", "godot", "unreal", "gamemaker", "construct"]),
            C(id="proto", tipo="habilidad", nombre="Prototipado y documentación (GDD)", peso=20,
              palabras_clave=["prototipo", "prototipado", "gdd", "game design document", "documentacion", "playtest", "playtesting"]),
            C(id="exp", tipo="experiencia", nombre="Experiencia en diseño o desarrollo de juegos (1 año)", peso=20,
              anios_min=1, palabras_clave=["game designer", "disenador de juegos", "disenadora de juegos", "level designer",
                                           "videojuegos", "desarrollador de juegos", "game developer", "diseno de juegos"]),
            C(id="en", tipo="idioma", nombre="Inglés intermedio", peso=15, idioma="ingles", nivel_idioma="intermedio",
              palabras_clave=["english"]),
        ],
    ),
    "tecnico_redes": Vacante(
        titulo="Técnico/a de redes · Proveedor de internet",
        descripcion="Instalación, configuración y mantenimiento de redes LAN/WAN y fibra óptica; soporte de nivel 2.",
        criterios=[
            C(id="exp", tipo="experiencia", nombre="Experiencia en redes (2 años)", peso=30, anios_min=2,
              palabras_clave=["redes", "red", "networking", "infraestructura", "telecomunicaciones", "fibra", "noc",
                              "soporte tecnico", "tecnico de campo", "ftth"]),
            C(id="conf", tipo="habilidad", nombre="Enrutamiento y conmutación (VLAN, OSPF, BGP)", peso=25,
              palabras_clave=["vlan", "ospf", "bgp", "enrutamiento", "routing", "switching", "stp", "mikrotik", "cisco ios"]),
            C(id="cert", tipo="habilidad", nombre="Certificación de redes (CCNA u otra)", peso=15,
              palabras_clave=["ccna", "ccnp", "mtcna", "network+", "fortinet nse", "huawei hcia", "jncia"]),
            C(id="fisica", tipo="habilidad", nombre="Cableado estructurado y fibra óptica", peso=15,
              palabras_clave=["cableado estructurado", "fibra optica", "fusion", "otdr", "ftth", "gpon", "cat6"]),
            C(id="form", tipo="formacion", nombre="Formación en redes o telecomunicaciones (tecnólogo)", peso=15,
              nivel_min="tecnologo", palabras_clave=["redes", "telecomunicaciones", "electronica", "sistemas", "informatica",
                                                    "computacion", "telematica"]),
        ],
    ),
}


def archivos(carpeta: str) -> list[Path]:
    """CV de una carpeta de seeds (se ignoran el aviso y el índice)."""
    return sorted((CARPETA / carpeta).glob("CV_*.pdf"))
