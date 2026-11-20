"""Estructuras de datos: lo que extrae el LLM y cómo se define una vacante."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

NivelFormacion = Literal["bachillerato", "tecnico", "tecnologo", "tercer_nivel", "cuarto_nivel", "otro"]
NivelIdioma = Literal["basico", "intermedio", "avanzado", "nativo"]

ORDEN_FORMACION = {"otro": 0, "bachillerato": 1, "tecnico": 2, "tecnologo": 3, "tercer_nivel": 4, "cuarto_nivel": 5}
ORDEN_IDIOMA = {"basico": 1, "intermedio": 2, "avanzado": 3, "nativo": 4}


# ---------------------------------------------------------------- extracción (salida del LLM)
class _Item(BaseModel):
    # extra="ignore": si el modelo agrega campos (p. ej. edad), se descartan al validar
    model_config = ConfigDict(extra="ignore")
    cita: str = Field(description="Frase copiada textualmente del CV que respalda este dato")


class Formacion(_Item):
    titulo: str
    institucion: str = ""
    nivel: NivelFormacion


class Experiencia(_Item):
    cargo: str
    empresa: str = ""
    inicio: str = Field(description="AAAA-MM o AAAA")
    fin: str = Field(description="AAAA-MM, AAAA o 'actual'")
    descripcion: str = ""


class Habilidad(_Item):
    nombre: str


class Idioma(_Item):
    idioma: str
    nivel: NivelIdioma


class Proyecto(_Item):
    nombre: str
    descripcion: str = ""


class ExtraccionCV(BaseModel):
    model_config = ConfigDict(extra="ignore")
    nombre_candidato: str
    formacion: list[Formacion]
    experiencia: list[Experiencia]
    habilidades: list[Habilidad]
    idiomas: list[Idioma]
    proyectos: list[Proyecto]


def esquema_json_estricto(modelo: type[BaseModel]) -> dict:
    """Esquema JSON con additionalProperties=false en todos los objetos.

    LM Studio lo convierte en una gramática: el modelo no puede generar
    campos fuera del esquema (por ejemplo, edad o estado civil)."""
    esquema = modelo.model_json_schema()

    def cerrar(nodo):
        if isinstance(nodo, dict):
            if nodo.get("type") == "object":
                nodo["additionalProperties"] = False
                nodo["required"] = list(nodo.get("properties", {}).keys())
            for v in nodo.values():
                cerrar(v)
        elif isinstance(nodo, list):
            for v in nodo:
                cerrar(v)

    cerrar(esquema)
    return esquema


# ---------------------------------------------------------------- vacante y criterios
TipoCriterio = Literal["habilidad", "experiencia", "formacion", "idioma"]


class Criterio(BaseModel):
    id: str
    tipo: TipoCriterio
    nombre: str
    peso: float = Field(gt=0, le=100)
    palabras_clave: list[str] = []  # sinónimos aceptados (habilidad, experiencia, área de formación)
    anios_min: float = 0  # experiencia
    nivel_min: NivelFormacion | None = None  # formación
    idioma: str | None = None  # idioma
    nivel_idioma: NivelIdioma | None = None

    @model_validator(mode="after")
    def _campos_por_tipo(self):
        if self.tipo in ("habilidad",) and not self.palabras_clave:
            raise ValueError(f"'{self.nombre}': una habilidad necesita al menos una palabra clave")
        if self.tipo == "experiencia" and self.anios_min <= 0:
            raise ValueError(f"'{self.nombre}': indique los años mínimos de experiencia")
        if self.tipo == "formacion" and not self.nivel_min:
            raise ValueError(f"'{self.nombre}': indique el nivel mínimo de formación")
        if self.tipo == "idioma" and not (self.idioma and self.nivel_idioma):
            raise ValueError(f"'{self.nombre}': indique el idioma y el nivel")
        return self


class Vacante(BaseModel):
    id: int | None = None
    titulo: str
    descripcion: str = ""
    criterios: list[Criterio]

    @model_validator(mode="after")
    def _pesos(self):
        if not self.criterios:
            raise ValueError("La vacante necesita al menos un criterio")
        total = sum(c.peso for c in self.criterios)
        if abs(total - 100) > 0.01:
            raise ValueError(f"Los pesos deben sumar 100 % (ahora suman {total:g} %)")
        ids = [c.id for c in self.criterios]
        if len(ids) != len(set(ids)):
            raise ValueError("Hay criterios con el mismo id")
        from .equidad import terminos_sensibles  # evita import circular
        for c in self.criterios:
            sens = terminos_sensibles(" ".join([c.nombre, *c.palabras_clave]))
            if sens:
                raise ValueError(f"El criterio '{c.nombre}' usa datos personales que no se pueden "
                                 f"evaluar ({', '.join(sens)}). Use solo competencias y experiencia.")
        return self


# ---------------------------------------------------------------- resultado
Estado = Literal["cumple", "parcial", "no_identificado"]
VALOR_ESTADO = {"cumple": 1.0, "parcial": 0.5, "no_identificado": 0.0}


class ResultadoCriterio(BaseModel):
    criterio_id: str
    nombre: str
    peso: float
    estado: Estado
    detalle: str
    citas: list[str] = []
    corregido: bool = False

    @property
    def s(self) -> float:
        return VALOR_ESTADO[self.estado]
