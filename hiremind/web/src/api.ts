// Cliente de la API local (FastAPI). Los tipos reflejan agente/modelos.py.

export type TipoCriterio = "habilidad" | "experiencia" | "formacion" | "idioma";
export type NivelFormacion = "bachillerato" | "tecnico" | "tecnologo" | "tercer_nivel" | "cuarto_nivel" | "otro";
export type NivelIdioma = "basico" | "intermedio" | "avanzado" | "nativo";
export type Estado = "cumple" | "parcial" | "no_identificado";

export interface Criterio {
  id: string;
  tipo: TipoCriterio;
  nombre: string;
  peso: number;
  palabras_clave: string[];
  anios_min: number;
  nivel_min: NivelFormacion | null;
  idioma: string | null;
  nivel_idioma: NivelIdioma | null;
}

export interface Vacante {
  id: number | null;
  titulo: string;
  descripcion: string;
  criterios: Criterio[];
  creada?: string;
  evaluados?: number;
  revision?: number;
  mejor?: number | null;
  promedio?: number | null;
  ultima_actividad?: string | null;
}

export interface ResultadoCriterio {
  criterio_id: string;
  nombre: string;
  peso: number;
  estado: Estado;
  detalle: string;
  citas: string[];
  corregido: boolean;
}

type ItemExtraido = { cita: string; verificado?: boolean } & Record<string, unknown>;

export type TipoPregunta = "tecnica" | "experiencia" | "situacional" | "verificacion";
export interface Pregunta {
  pregunta: string;
  criterio: string;
  tipo: TipoPregunta;
  proposito: string;
}

export interface SeleccionCandidato {
  correo: string;
  correo_enviado: string | null;
  creada: string;
  preguntas: Pregunta[];
  origen_preguntas: "llm" | "plantilla" | "";
}

export interface BorradorSeleccion {
  correo_sugerido: string;
  asunto: string;
  texto: string;
  correo_configurado: boolean;
  remitente: string;
  redirigir_a: string;
}

export interface Candidato {
  id: number;
  eval_id: number;
  posicion: number;
  top: boolean;
  archivo: string;
  nombre: string;
  puntaje: number;
  justificacion: string;
  segundos: number;
  intentos: number;
  corregida: number;
  datos_quitados: string[];
  seleccion: SeleccionCandidato | null;
  criterios: ResultadoCriterio[];
  extraccion: Record<"formacion" | "experiencia" | "habilidades" | "idiomas" | "proyectos", ItemExtraido[]> & {
    nombre_candidato: string;
  };
}

export interface RevisionManual {
  id: number;
  archivo: string;
  motivo: string;
  creado: string;
}

export interface Ranking {
  candidatos: Candidato[];
  revision_manual: RevisionManual[];
  top_n: number;
}

export interface ResultadoCV {
  archivo: string;
  estado: "evaluado" | "revision_manual";
  motivo: string;
  nombre: string;
  puntaje: number;
  segundos: number;
  intentos: number;
  no_verificados: number;
  datos_quitados: string[];
}

export interface EstadoServidor {
  llm_ok: boolean;
  mensaje: string;
  modelo: string;
  url: string;
  top_n: number;
}

export interface Resumen {
  vacantes: number;
  evaluados: number;
  revision: number;
  segundos_promedio: number | null;
  corregidas: number;
  distribucion: { rango: string; cantidad: number }[];
  recientes: {
    id: number;
    nombre: string;
    archivo: string;
    estado: "evaluado" | "revision_manual";
    creado: string;
    vacante_id: number;
    vacante: string;
    puntaje: number | null;
  }[];
  por_vacante: Vacante[];
}

export class ErrorApi extends Error {
  constructor(public errores: string[], public status: number) {
    super(errores.join(" · "));
  }
}

async function pedir<T>(ruta: string, init?: RequestInit): Promise<T> {
  let r: Response;
  try {
    r = await fetch(`/api${ruta}`, init);
  } catch {
    throw new ErrorApi(["No se pudo conectar con la API local (¿está encendido el servidor en el puerto 8000?)"], 0);
  }
  if (r.status === 204) return undefined as T;
  const cuerpo = await r.json().catch(() => ({}));
  if (!r.ok) {
    const errores: string[] = cuerpo.errores ?? [
      typeof cuerpo.detail === "string" ? cuerpo.detail : `Error ${r.status}`,
    ];
    throw new ErrorApi(errores, r.status);
  }
  return cuerpo as T;
}

const json = (metodo: string, datos: unknown): RequestInit => ({
  method: metodo,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(datos),
});

export const api = {
  estado: () => pedir<EstadoServidor>("/estado"),
  resumen: () => pedir<Resumen>("/resumen"),
  vacantes: () => pedir<Vacante[]>("/vacantes"),
  vacante: (id: number) => pedir<Vacante>(`/vacantes/${id}`),
  guardarVacante: (v: Vacante) =>
    v.id ? pedir<Vacante>(`/vacantes/${v.id}`, json("PUT", v)) : pedir<Vacante>("/vacantes", json("POST", v)),
  borrarVacante: (id: number) => pedir<void>(`/vacantes/${id}`, { method: "DELETE" }),
  cargarDemo: () => pedir<{ creadas: number }>("/vacantes/demo", { method: "POST" }),
  subirCV: (vacanteId: number, archivo: File) => {
    const fd = new FormData();
    fd.append("archivo", archivo);
    return pedir<ResultadoCV>(`/vacantes/${vacanteId}/cvs`, { method: "POST", body: fd });
  },
  ranking: (id: number) => pedir<Ranking>(`/vacantes/${id}/ranking`),
  corregir: (evalId: number, criterioId: string, estado: Estado) =>
    pedir<{ puntaje: number }>(`/evaluaciones/${evalId}/criterios/${criterioId}`, json("PATCH", { estado })),
  borradorSeleccion: (candidatoId: number) => pedir<BorradorSeleccion>(`/candidatos/${candidatoId}/seleccion/borrador`),
  seleccionar: (candidatoId: number, datos: { correo: string; mensaje: string; enviar_correo: boolean }) =>
    pedir<SeleccionCandidato>(`/candidatos/${candidatoId}/seleccionar`, json("POST", datos)),
  regenerarPreguntas: (candidatoId: number) =>
    pedir<Pick<SeleccionCandidato, "preguntas" | "origen_preguntas">>(`/candidatos/${candidatoId}/preguntas`, { method: "POST" }),
  quitarSeleccion: (candidatoId: number) => pedir<void>(`/candidatos/${candidatoId}/seleccion`, { method: "DELETE" }),
  urlCSV: (id: number) => `/api/vacantes/${id}/ranking.csv`,
  urlPDF: (candidatoId: number) => `/api/candidatos/${candidatoId}/pdf`,
};

// ---------------------------------------------------------------- textos
export const NOMBRE_ESTADO: Record<Estado, string> = {
  cumple: "Cumple",
  parcial: "Parcial",
  no_identificado: "No identificado",
};
export const NOMBRE_TIPO: Record<TipoCriterio, string> = {
  habilidad: "Habilidad",
  experiencia: "Experiencia",
  formacion: "Formación",
  idioma: "Idioma",
};
export const NOMBRE_NIVEL: Record<NivelFormacion, string> = {
  bachillerato: "Bachillerato",
  tecnico: "Técnico",
  tecnologo: "Tecnólogo",
  tercer_nivel: "Tercer nivel",
  cuarto_nivel: "Cuarto nivel",
  otro: "Curso u otro",
};
export const NOMBRE_IDIOMA: Record<NivelIdioma, string> = {
  basico: "Básico (A1–A2)",
  intermedio: "Intermedio (B1–B2)",
  avanzado: "Avanzado (C1–C2)",
  nativo: "Nativo",
};
