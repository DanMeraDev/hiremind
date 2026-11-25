// Elegir al candidato: correo de aviso + preguntas sugeridas para la entrevista.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { Check, Copy, Mail, MessageCircleQuestion, RefreshCw, Send, UserCheck, X } from "lucide-react";
import { useEffect, useState, type CSSProperties } from "react";
import { api, ErrorApi, type Candidato, type TipoPregunta } from "../api";
import { Aviso, Insignia, fechaCorta } from "../components/ui";

const NOMBRE_TIPO: Record<TipoPregunta, string> = {
  tecnica: "Técnica",
  experiencia: "Experiencia",
  situacional: "Situacional",
  verificacion: "Verificar",
};
const TONO_TIPO = { tecnica: "marca", experiencia: "verde", situacional: "neutro", verificacion: "ambar" } as const;

function Formulario({ c, vid, cerrar }: { c: Candidato; vid: number; cerrar: () => void }) {
  const qc = useQueryClient();
  const { data: b, isLoading } = useQuery({ queryKey: ["borrador", c.id], queryFn: () => api.borradorSeleccion(c.id) });
  const [correo, setCorreo] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [enviar, setEnviar] = useState(true);
  useEffect(() => {
    if (b) { setCorreo((x) => x || b.correo_sugerido); setEnviar(b.correo_configurado); }
  }, [b]);
  const confirmar = useMutation({
    mutationFn: () => api.seleccionar(c.id, { correo, mensaje, enviar_correo: enviar }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ranking", vid] }),
  });

  return (
    <div className="a-sube mt-4 space-y-3 border-t-2 border-(--tinta) pt-4">
      <div>
        <label className="etiqueta" htmlFor="correo-candidato">Correo del candidato</label>
        <input id="correo-candidato" type="email" className="campo" value={correo} autoFocus
          onChange={(e) => setCorreo(e.target.value)} placeholder="nombre@correo.com" />
        {b && !b.correo_sugerido && (
          <p className="mt-1 text-xs text-zinc-500">No encontramos un correo en el CV: escríbalo usted.</p>
        )}
      </div>
      <div>
        <label className="etiqueta" htmlFor="mensaje-candidato">Mensaje adicional (opcional)</label>
        <textarea id="mensaje-candidato" rows={2} className="campo resize-y" value={mensaje}
          onChange={(e) => setMensaje(e.target.value)} placeholder="Ej.: La entrevista será presencial en nuestras oficinas." />
      </div>
      {isLoading ? <p className="text-xs text-zinc-500">Preparando la vista previa…</p> : b && (
        <details className="border-2 border-zinc-200 dark:border-zinc-700">
          <summary className="cursor-pointer px-3 py-2 text-xs font-bold">Vista previa del correo</summary>
          <div className="border-t-2 border-zinc-200 px-3 py-2 text-xs dark:border-zinc-700">
            <p><span className="font-bold">De:</span> {b.remitente || "—"}</p>
            <p><span className="font-bold">Asunto:</span> {b.asunto}</p>
            <pre className="mt-2 whitespace-pre-wrap font-sans leading-relaxed text-zinc-700 dark:text-zinc-300">
              {mensaje.trim() ? b.texto.replace("En los próximos días", `${mensaje.trim()}\n\nEn los próximos días`) : b.texto}
            </pre>
          </div>
        </details>
      )}
      <label className={clsx("flex items-center gap-2 text-sm font-semibold", !b?.correo_configurado && "opacity-60")}>
        <input type="checkbox" checked={enviar} disabled={!b?.correo_configurado} onChange={(e) => setEnviar(e.target.checked)}
          className="size-4 accent-coral" />
        Enviar el correo ahora
      </label>
      {b?.correo_configurado && b.redirigir_a && enviar && (
        <Aviso tono="marca">Modo prueba: el correo se enviará a <strong>{b.redirigir_a}</strong>, no al candidato.</Aviso>
      )}
      {b && !b.correo_configurado && <Aviso tono="ambar">El correo no está configurado (falta <code>hiremind/.env</code>). Se guardará la selección sin enviar nada.</Aviso>}
      {confirmar.error && <Aviso>{(confirmar.error as ErrorApi).message}</Aviso>}
      {confirmar.isPending && (
        <p className="text-xs font-semibold text-zinc-500" role="status">
          {enviar ? "Enviando el correo y preparando las preguntas…" : "Preparando las preguntas…"} (el modelo local puede tardar unos segundos)
        </p>
      )}
      <div className="flex flex-wrap gap-2">
        <button type="button" className="btn-primario" disabled={confirmar.isPending || !correo.trim()} onClick={() => confirmar.mutate()}>
          {enviar ? <><Send className="size-4" /> Confirmar y enviar</> : <><Check className="size-4" /> Confirmar selección</>}
        </button>
        <button type="button" className="btn-fantasma" disabled={confirmar.isPending} onClick={cerrar}>Cancelar</button>
      </div>
    </div>
  );
}

function Preguntas({ c, vid }: { c: Candidato; vid: number }) {
  const qc = useQueryClient();
  const sel = c.seleccion!;
  const [copiado, setCopiado] = useState(false);
  const regenerar = useMutation({
    mutationFn: () => api.regenerarPreguntas(c.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ranking", vid] }),
  });
  const quitar = useMutation({
    mutationFn: () => api.quitarSeleccion(c.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ranking", vid] }),
  });
  const copiar = () => {
    const txt = sel.preguntas.map((p, i) => `${i + 1}. ${p.pregunta}\n   (${p.criterio} · ${p.proposito})`).join("\n");
    navigator.clipboard?.writeText(`Entrevista · ${c.nombre}\n\n${txt}`).then(() => { setCopiado(true); setTimeout(() => setCopiado(false), 1500); });
  };

  return (
    <section className="tarjeta a-sube overflow-hidden" style={{ "--i": 1 } as CSSProperties}>
      <div className="flex flex-wrap items-center gap-3 border-b-2 border-(--tinta) bg-menta px-5 py-3 text-noche">
        <UserCheck className="size-5" />
        <div className="min-w-0 flex-1">
          <p className="font-titulo text-2xl leading-none">Candidato seleccionado</p>
          <p className="mt-1 flex items-center gap-1 text-xs font-semibold">
            <Mail className="size-3.5" />
            {sel.correo_enviado ? <>Correo enviado a {sel.correo} · {fechaCorta(sel.correo_enviado)}</> : <>Sin correo enviado ({sel.correo})</>}
          </p>
        </div>
        <button type="button" className="btn-fantasma px-2 py-1 text-xs text-noche hover:bg-white/60" disabled={quitar.isPending}
          onClick={() => confirm("¿Quitar la selección? El correo ya enviado no se puede deshacer.") && quitar.mutate()}>
          <X className="size-3.5" /> Quitar
        </button>
      </div>
      <div className="p-5">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <h3 className="flex items-center gap-2 font-titulo text-2xl">
            <MessageCircleQuestion className="size-5 text-coral" /> Preguntas para la entrevista
          </h3>
          <span className="ml-auto flex gap-1">
            <button type="button" className="btn-fantasma px-2 py-1 text-xs" onClick={copiar}>
              {copiado ? <Check className="size-3.5" /> : <Copy className="size-3.5" />} {copiado ? "Copiadas" : "Copiar"}
            </button>
            <button type="button" className="btn-fantasma px-2 py-1 text-xs" disabled={regenerar.isPending} onClick={() => regenerar.mutate()}>
              <RefreshCw className={clsx("size-3.5", regenerar.isPending && "animate-spin")} /> {regenerar.isPending ? "Generando…" : "Otras preguntas"}
            </button>
          </span>
        </div>
        <p className="mb-3 text-xs text-zinc-500">
          {sel.origen_preguntas === "llm"
            ? "Generadas por el modelo local con los criterios del puesto y la evidencia verificada del CV (sin datos personales)."
            : "Armadas con una plantilla según los criterios (el modelo local no estaba disponible)."}
        </p>
        <ol className="space-y-2.5">
          {sel.preguntas.map((p, i) => (
            <li key={i} style={{ "--i": i } as CSSProperties} className="a-entra flex gap-3 border-l-4 border-azul bg-zinc-50 px-3 py-2.5 dark:bg-zinc-800/60">
              <span className="font-titulo text-xl leading-none text-coral">{i + 1}</span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold leading-snug">{p.pregunta}</p>
                <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-xs text-zinc-500">
                  <Insignia tono={TONO_TIPO[p.tipo]}>{NOMBRE_TIPO[p.tipo]}</Insignia>
                  <span className="font-semibold">{p.criterio}</span>
                  <span>· {p.proposito}</span>
                </div>
              </div>
            </li>
          ))}
        </ol>
        {regenerar.error && <div className="mt-3"><Aviso>{(regenerar.error as ErrorApi).message}</Aviso></div>}
      </div>
    </section>
  );
}

export default function SeleccionCandidato({ c, vid }: { c: Candidato; vid: number }) {
  const [abierto, setAbierto] = useState(false);
  useEffect(() => setAbierto(false), [c.id]);
  if (c.seleccion) return <Preguntas c={c} vid={vid} />;
  return (
    <section className="tarjeta a-sube p-5" style={{ "--i": 1 } as CSSProperties}>
      <div className="flex flex-wrap items-center gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="font-titulo text-2xl">¿Avanza a entrevista?</h3>
          <p className="text-xs text-zinc-500">Al seleccionarlo se le envía un correo con el puesto y se preparan preguntas para la entrevista.</p>
        </div>
        {!abierto && (
          <button type="button" className="btn-primario" onClick={() => setAbierto(true)}>
            <UserCheck className="size-4" /> Seleccionar candidato
          </button>
        )}
      </div>
      {abierto && <Formulario c={c} vid={vid} cerrar={() => setAbierto(false)} />}
    </section>
  );
}
