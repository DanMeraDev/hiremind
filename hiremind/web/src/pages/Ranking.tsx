import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import {
  BadgeCheck, ChevronDown, Download, ExternalLink, EyeOff, FileUp, Pencil, Quote, ScanLine, Search, Star, Trophy, UserCheck,
} from "lucide-react";
import { useMemo, useRef, useState, type CSSProperties } from "react";
import { Link, useParams } from "react-router";
import { api, NOMBRE_ESTADO, type Candidato, type Estado, type ResultadoCriterio } from "../api";
import { PestanasVacante } from "../components/Layout";
import { AnilloPuntaje, BarraPuntaje, Cargando, Insignia, InsigniaEstado, PuntoEstado, Vacio, fmt } from "../components/ui";

const ESTADOS: Estado[] = ["cumple", "parcial", "no_identificado"];

function Criterio({ r, evalId, vid }: { r: ResultadoCriterio; evalId: number; vid: number }) {
  const qc = useQueryClient();
  const corregir = useMutation({
    mutationFn: (e: Estado) => api.corregir(evalId, r.criterio_id, e),
    onSuccess: () => { setDestello((n) => n + 1); qc.invalidateQueries({ queryKey: ["ranking", vid] }); },
  });
  const [destello, setDestello] = useState(0);
  return (
    <li key={destello} className={clsx("-mx-2 px-2 py-4 first:pt-2 last:pb-2", destello > 0 && "a-destello")}>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm font-bold">{r.nombre}</span>
        <span className="border-[1.5px] border-zinc-300 px-1 text-[11px] font-bold tabular-nums text-zinc-500 dark:border-zinc-600">{r.peso} %</span>
        <span className="ml-auto flex items-center gap-1.5">
          {r.corregido && <Insignia tono="marca"><Pencil className="size-3" /> Corregido</Insignia>}
          <InsigniaEstado estado={r.estado} />
        </span>
      </div>
      <p className="mt-1 text-xs font-medium text-zinc-500">{r.detalle}</p>
      {r.citas.length > 0 && (
        <div className="mt-2.5 space-y-1.5">
          {r.citas.slice(0, 3).map((c, i) => (
            <blockquote key={c} style={{ "--i": i } as CSSProperties} className="a-entra flex gap-2 border-l-4 border-menta bg-zinc-50 px-3 py-2 text-xs leading-relaxed text-zinc-700 dark:bg-zinc-800/60 dark:text-zinc-200">
              <Quote className="mt-0.5 size-3 shrink-0 text-coral" />
              <span className="flex-1">{c}</span>
              <BadgeCheck className="mt-0.5 size-3.5 shrink-0 text-emerald-600 dark:text-menta" aria-label="Cita verificada en el CV" />
            </blockquote>
          ))}
        </div>
      )}
      <div className="mt-2.5 flex items-center gap-2">
        <span className="text-[11px] font-extrabold uppercase italic text-zinc-500">Corregir</span>
        <div className="inline-flex border-2 border-(--tinta) bg-white dark:bg-zinc-900">
          {ESTADOS.map((e) => (
            <button key={e} type="button" disabled={corregir.isPending}
              onClick={() => e !== r.estado && corregir.mutate(e)}
              className={clsx(
                "border-r-2 border-(--tinta) px-2 py-0.5 text-[11px] font-bold uppercase transition-colors last:border-r-0",
                e === r.estado
                  ? { cumple: "bg-menta text-noche", parcial: "bg-ambar text-noche", no_identificado: "bg-zinc-200 text-noche dark:bg-zinc-700 dark:text-white" }[e]
                  : "text-zinc-500 hover:bg-zinc-100 hover:text-noche dark:hover:bg-zinc-800 dark:hover:text-white",
              )}>
              {NOMBRE_ESTADO[e]}
            </button>
          ))}
        </div>
      </div>
    </li>
  );
}

const SECCIONES = [
  ["formacion", "Formación", (x: Record<string, unknown>) => `${x.titulo}`],
  ["experiencia", "Experiencia", (x: Record<string, unknown>) => `${x.cargo}${x.empresa ? ` · ${x.empresa}` : ""} (${x.inicio} – ${x.fin})`],
  ["habilidades", "Habilidades", (x: Record<string, unknown>) => `${x.nombre}`],
  ["idiomas", "Idiomas", (x: Record<string, unknown>) => `${x.idioma} · ${x.nivel}`],
  ["proyectos", "Proyectos", (x: Record<string, unknown>) => `${x.nombre}`],
] as const;

function DatosExtraidos({ c }: { c: Candidato }) {
  const [abierto, setAbierto] = useState(false);
  const total = SECCIONES.reduce((s, [k]) => s + c.extraccion[k].length, 0);
  const sinVerificar = SECCIONES.reduce((s, [k]) => s + c.extraccion[k].filter((x) => x.verificado === false).length, 0);
  return (
    <div className="tarjeta">
      <button type="button" onClick={() => setAbierto(!abierto)} className="flex w-full items-center justify-between px-5 py-3.5 text-left">
        <span className="font-titulo text-2xl">Datos extraídos por el modelo</span>
        <span className="flex items-center gap-2 text-xs font-semibold text-zinc-500">
          {total} datos{sinVerificar > 0 && <Insignia tono="rojo">{sinVerificar} sin verificar</Insignia>}
          <ChevronDown className={clsx("size-4 transition-transform duration-300 ease-rebote", abierto && "rotate-180")} />
        </span>
      </button>
      {abierto && (
        <div className="a-sube space-y-4 border-t-2 border-(--tinta) px-5 py-4">
          {SECCIONES.map(([k, titulo, txt]) => c.extraccion[k].length > 0 && (
            <div key={k}>
              <p className="mb-1.5 text-[11px] font-extrabold uppercase italic tracking-wider text-zinc-500">{titulo}</p>
              <ul className="space-y-1">
                {c.extraccion[k].map((x, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    {x.verificado === false
                      ? <span title="La cita no aparece en el CV: no cuenta para el puntaje" className="mt-1 size-2.5 shrink-0 border-[1.5px] border-noche bg-coral" />
                      : <span title="Cita verificada" className="mt-1 size-2.5 shrink-0 border-[1.5px] border-noche bg-menta" />}
                    <span className={clsx(x.verificado === false && "text-zinc-400 line-through")}>{txt(x)}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
          <p className="text-xs text-zinc-500">Un dato tachado tenía una cita que no aparece en el CV: no se usa para el puntaje.</p>
        </div>
      )}
    </div>
  );
}

function Detalle({ c, vid }: { c: Candidato; vid: number }) {
  return (
    <div key={c.id} className="space-y-4">
      <section className="tarjeta a-sube relative overflow-hidden p-5">
        {c.top && <span aria-hidden className="absolute right-0 top-0 h-2 w-24 bg-coral" />}
        <div className="flex items-start gap-4">
          <AnilloPuntaje puntaje={c.puntaje} />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-1.5">
              <Insignia tono="neutro">#{c.posicion}</Insignia>
              {c.top && <Insignia tono="marca"><Star className="size-3 fill-current" /> Top para revisión</Insignia>}
              {!!c.corregida && <Insignia tono="marca"><Pencil className="size-3" /> Corregido</Insignia>}
            </div>
            <h2 className="mt-1.5 truncate font-titulo text-4xl">{c.nombre}</h2>
            <a href={api.urlPDF(c.id)} target="_blank" rel="noreferrer" className="mt-0.5 inline-flex items-center gap-1 text-xs font-semibold text-zinc-500 underline decoration-2 underline-offset-2 hover:text-marca-700 dark:hover:text-marca-300">
              {c.archivo} <ExternalLink className="size-3" />
            </a>
          </div>
        </div>
        <div className="mt-4 border-2 border-(--tinta) bg-azul-claro p-3.5 dark:bg-marca-950">
          <p className="mb-1 text-[11px] font-extrabold uppercase italic tracking-wider text-noche dark:text-marca-200">Justificación</p>
          <p className="text-sm font-medium leading-relaxed text-noche dark:text-zinc-100">{c.justificacion}</p>
        </div>
        {c.datos_quitados.length > 0 && (
          <p className="mt-3 flex items-start gap-1.5 text-xs text-zinc-500">
            <EyeOff className="mt-0.5 size-3.5 shrink-0" />
            Se excluyeron antes del análisis: {c.datos_quitados.join(", ")}.
          </p>
        )}
      </section>

      <section className="tarjeta a-sube p-5" style={{ "--i": 2 } as CSSProperties}>
        <h3 className="mb-3 font-titulo text-2xl">Evaluación por criterio</h3>
        <ul className="divide-y-2 divide-zinc-100 dark:divide-zinc-800">
          {c.criterios.map((r) => <Criterio key={r.criterio_id} r={r} evalId={c.eval_id} vid={vid} />)}
        </ul>
      </section>

      <DatosExtraidos c={c} />
    </div>
  );
}

export default function Ranking() {
  const vid = Number(useParams().id);
  const { data: vac } = useQuery({ queryKey: ["vacante", vid], queryFn: () => api.vacante(vid) });
  const { data, isLoading } = useQuery({ queryKey: ["ranking", vid], queryFn: () => api.ranking(vid) });
  const [sel, setSel] = useState<number | null>(null);
  const [filtro, setFiltro] = useState("");
  const detalle = useRef<HTMLDivElement>(null);
  const elegir = (id: number) => {
    setSel(id);
    // en pantallas angostas el detalle queda debajo de la lista: llevar la vista hasta él
    if (window.innerWidth < 1024) setTimeout(() => detalle.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 0);
  };

  const lista = useMemo(
    () => (data?.candidatos ?? []).filter((c) => `${c.nombre} ${c.archivo}`.toLowerCase().includes(filtro.toLowerCase())),
    [data, filtro],
  );
  if (isLoading || !data || !vac) return <Cargando />;
  const actual = data.candidatos.find((c) => c.id === sel) ?? lista[0];

  return (
    <>
      <PestanasVacante id={vid} titulo={vac.titulo} evaluados={vac.evaluados} />

      {data.candidatos.length === 0 && data.revision_manual.length === 0 ? (
        <Vacio icono={<Trophy className="size-5" />} titulo="Sin candidatos evaluados"
          texto="Suba hojas de vida para generar el ranking de esta vacante."
          accion={<Link to={`/app/vacantes/${vid}/cvs`} className="btn-primario"><FileUp className="size-4" /> Subir hojas de vida</Link>} />
      ) : (
        <>
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="flex items-start gap-2 text-sm text-zinc-600 dark:text-zinc-400">
              <UserCheck className="mt-0.5 size-4 shrink-0 text-coral" />
              <span className="font-medium">Se ordenan <strong className="font-extrabold text-noche dark:text-zinc-100">todos</strong> los CV; nadie queda descartado.
                Revise el top {data.top_n} y decida usted.</span>
            </div>
            <div className="flex gap-2 sm:ml-auto">
              <div className="relative">
                <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-zinc-400" />
                <input className="campo w-44 py-1.5 pl-8" placeholder="Buscar" value={filtro} onChange={(e) => setFiltro(e.target.value)} />
              </div>
              <a href={api.urlCSV(vid)} className="btn-secundario py-1.5"><Download className="size-4" /> CSV</a>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)]">
            <div className="space-y-4">
              <ul className="tarjeta divide-y-2 divide-zinc-100 overflow-hidden dark:divide-zinc-800">
                {lista.map((c, i) => (
                  <li key={c.id} className="a-entra" style={{ "--i": i } as CSSProperties}>
                    <button type="button" onClick={() => elegir(c.id)}
                      className={clsx(
                        "group flex w-full items-center gap-3 border-l-[6px] px-4 py-3 text-left transition-colors",
                        actual?.id === c.id ? "border-coral bg-menta-claro dark:bg-marca-950" : "border-transparent hover:bg-zinc-50 dark:hover:bg-zinc-800/50",
                      )}>
                      <span className={clsx("flex size-8 shrink-0 items-center justify-center border-2 font-titulo text-lg transition-transform duration-200 ease-rebote group-hover:-rotate-6",
                        c.top ? "border-(--tinta) bg-coral text-noche shadow-xs" : "border-zinc-300 bg-white text-zinc-500 dark:border-zinc-600 dark:bg-zinc-900")}>
                        {c.posicion}
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-1.5">
                          <span className="truncate text-sm font-bold">{c.nombre}</span>
                          {c.top && <Star className="size-3.5 shrink-0 fill-ambar text-noche dark:text-ambar" aria-label="Top" />}
                          {!!c.corregida && <Pencil className="size-3 shrink-0 text-marca-500" aria-label="Corregido" />}
                        </div>
                        <div className="mt-1.5 flex gap-1">
                          {c.criterios.map((r, j) => <PuntoEstado key={r.criterio_id} estado={r.estado} titulo={r.nombre} i={i + j} />)}
                        </div>
                      </div>
                      <div className="w-20 shrink-0 text-right">
                        <span className="font-titulo text-2xl leading-none">{fmt(c.puntaje)}</span>
                        <BarraPuntaje puntaje={c.puntaje} className="mt-1" i={i} />
                      </div>
                    </button>
                  </li>
                ))}
                {lista.length === 0 && <li className="px-4 py-6 text-center text-sm text-zinc-500">Sin resultados</li>}
              </ul>

              {data.revision_manual.length > 0 && (
                <section className="tarjeta a-sube p-4">
                  <h3 className="flex items-center gap-2 font-titulo text-2xl">
                    <ScanLine className="size-5 text-amber-600 dark:text-ambar" /> Revisión manual
                    <span className="text-xs font-normal text-zinc-500">· {data.revision_manual.length}</span>
                  </h3>
                  <p className="mt-0.5 text-xs text-zinc-500">El agente no pudo leerlos. Una persona debe revisarlos directamente.</p>
                  <ul className="mt-3 space-y-2">
                    {data.revision_manual.map((m) => (
                      <li key={m.id} className="flex items-center gap-3 border-l-4 border-ambar bg-amber-50 px-3 py-2 text-sm dark:bg-amber-950">
                        <div className="min-w-0 flex-1">
                          <p className="truncate font-medium">{m.archivo}</p>
                          <p className="truncate text-xs text-zinc-500">{m.motivo}</p>
                        </div>
                        <a href={api.urlPDF(m.id)} target="_blank" rel="noreferrer" className="btn-fantasma px-2 py-1 text-xs">
                          Abrir <ExternalLink className="size-3" />
                        </a>
                      </li>
                    ))}
                  </ul>
                </section>
              )}
              <p className="flex items-center gap-3 px-1 text-xs font-semibold text-zinc-500">
                <span className="flex items-center gap-1"><PuntoEstado estado="cumple" titulo="" /> Cumple</span>
                <span className="flex items-center gap-1"><PuntoEstado estado="parcial" titulo="" /> Parcial</span>
                <span className="flex items-center gap-1"><PuntoEstado estado="no_identificado" titulo="" /> No identificado</span>
              </p>
            </div>

            <div ref={detalle} className="scroll-mt-16 lg:sticky lg:top-8 lg:self-start">
              {actual ? <Detalle c={actual} vid={vid} /> : <p className="text-sm text-zinc-500">Seleccione un candidato.</p>}
            </div>
          </div>
        </>
      )}
    </>
  );
}
