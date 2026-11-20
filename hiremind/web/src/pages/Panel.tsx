import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Briefcase, Clock, FileText, Pencil, ScanLine, Sparkles, Trophy } from "lucide-react";
import clsx from "clsx";
import type { CSSProperties, ReactNode } from "react";
import { Cifra } from "../components/anim";
import { Link } from "react-router";
import { api } from "../api";
import { BarraPuntaje, Cargando, Encabezado, Insignia, Vacio, fechaCorta, fmt } from "../components/ui";

const FONDO_KPI = ["bg-menta", "bg-coral", "bg-ambar", "bg-azul"];

function Kpi({ icono, etiqueta, valor, nota, i }: { icono: ReactNode; etiqueta: string; valor: ReactNode; nota?: string; i: number }) {
  return (
    <div className="tarjeta a-sube group relative overflow-hidden p-4 transition-transform duration-200 ease-rebote hover:-translate-y-1" style={{ "--i": i } as CSSProperties}>
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-extrabold uppercase italic tracking-wider text-zinc-500">{etiqueta}</span>
        <span className={clsx("flex size-7 items-center justify-center border-2 border-(--tinta) text-noche transition-transform duration-300 ease-rebote group-hover:rotate-6", FONDO_KPI[i])}>{icono}</span>
      </div>
      <div className="mt-2 font-titulo text-5xl">{valor}</div>
      {nota && <p className="mt-0.5 text-xs font-medium text-zinc-500">{nota}</p>}
    </div>
  );
}

export default function Panel() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["resumen"], queryFn: api.resumen });
  const demo = useMutation({
    mutationFn: api.cargarDemo,
    onSuccess: () => qc.invalidateQueries(),
  });

  if (isLoading || !data) return <Cargando />;
  const maxDist = Math.max(1, ...data.distribucion.map((d) => d.cantidad));

  return (
    <>
      <Encabezado
        titulo="Panel"
        descripcion="Resumen de los procesos de selección en este equipo."
        acciones={<Link to="/app/vacantes/nueva" className="btn-primario"><Briefcase className="size-4" /> Nueva vacante</Link>}
      />

      {data.vacantes === 0 ? (
        <Vacio
          icono={<Sparkles className="size-5" />}
          titulo="Todavía no hay vacantes"
          texto="Cree una vacante con sus criterios o cargue las 2 vacantes de ejemplo para probar el agente con los CV ficticios."
          accion={
            <div className="flex flex-wrap justify-center gap-2">
              <button className="btn-primario" onClick={() => demo.mutate()} disabled={demo.isPending}>
                <Sparkles className="size-4" /> Cargar vacantes de ejemplo
              </button>
              <Link to="/app/vacantes/nueva" className="btn-secundario">Crear vacante</Link>
            </div>
          }
        />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <Kpi i={0} icono={<Briefcase className="size-4" />} etiqueta="Vacantes" valor={<Cifra valor={data.vacantes} />} />
            <Kpi i={1} icono={<FileText className="size-4" />} etiqueta="CV evaluados" valor={<Cifra valor={data.evaluados} />}
              nota={data.corregidas ? `${data.corregidas} con corrección humana` : undefined} />
            <Kpi i={2} icono={<ScanLine className="size-4" />} etiqueta="Revisión manual" valor={<Cifra valor={data.revision} />} nota="Escaneados o ilegibles" />
            <Kpi i={3} icono={<Clock className="size-4" />} etiqueta="Tiempo por CV"
              valor={data.segundos_promedio != null ? <Cifra valor={Math.round(data.segundos_promedio * 10) / 10} decimales={1} sufijo=" s" /> : "—"} nota="Promedio, en este equipo" />
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <section className="tarjeta a-sube lg:col-span-2" style={{ "--i": 4 } as CSSProperties}>
              <div className="flex items-center justify-between border-b-2 border-(--tinta) px-4 py-3">
                <h2 className="font-titulo text-2xl">Procesos de selección</h2>
                <Link to="/app/vacantes" className="text-xs font-extrabold uppercase text-marca-700 underline decoration-2 underline-offset-4 hover:text-coral dark:text-marca-300">Ver todas</Link>
              </div>
              <ul className="divide-y-2 divide-zinc-100 dark:divide-zinc-800">
                {data.por_vacante.map((v, i) => (
                  <li key={v.id} className="a-entra flex flex-col gap-3 px-4 py-3.5 transition-colors hover:bg-zinc-50 sm:flex-row sm:items-center dark:hover:bg-zinc-800/50" style={{ "--i": i + 6 } as CSSProperties}>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-bold">{v.titulo}</p>
                      <p className="mt-0.5 text-xs text-zinc-500">
                        {v.criterios.length} criterios · {v.evaluados ?? 0} evaluados
                        {!!v.revision && <> · <span className="text-amber-600 dark:text-amber-400">{v.revision} en revisión manual</span></>}
                      </p>
                    </div>
                    <div className="w-full sm:w-40">
                      {v.mejor != null ? (
                        <>
                          <div className="mb-1 flex justify-between text-xs text-zinc-500">
                            <span className="font-semibold">Mejor puntaje</span><span className="font-titulo text-lg leading-none text-noche dark:text-zinc-100"><Cifra valor={v.mejor} /></span>
                          </div>
                          <BarraPuntaje puntaje={v.mejor} i={i + 6} />
                        </>
                      ) : <span className="text-xs text-zinc-400">Sin CV evaluados</span>}
                    </div>
                    <Link to={v.evaluados ? `/app/vacantes/${v.id}/ranking` : `/app/vacantes/${v.id}/cvs`} className="btn-secundario py-1.5 text-xs">
                      {v.evaluados ? <><Trophy className="size-3.5" /> Ranking</> : <>Subir CV <ArrowRight className="size-3.5" /></>}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>

            <section className="tarjeta a-sube p-4" style={{ "--i": 5 } as CSSProperties}>
              <h2 className="font-titulo text-2xl">Distribución de puntajes</h2>
              <p className="mt-0.5 text-xs text-zinc-500">Todos los CV evaluados</p>
              <div className="mt-5 flex h-40 items-end gap-3">
                {data.distribucion.map((d, i) => (
                  <div key={d.rango} className="flex h-full flex-1 flex-col items-center justify-end gap-1.5">
                    <span className="font-titulo text-xl leading-none"><Cifra valor={d.cantidad} /></span>
                    <div className={clsx("a-crece-y w-full border-2 border-(--tinta)", ["bg-zinc-300 dark:bg-zinc-600", "bg-ambar", "bg-azul", "bg-menta"][i] ?? "bg-azul")}
                      style={{ height: `${(d.cantidad / maxDist) * 100}%`, minHeight: d.cantidad ? 6 : 2, "--i": i } as CSSProperties} />
                    <span className="text-[11px] font-semibold tabular-nums text-zinc-500">{d.rango}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <section className="tarjeta a-sube" style={{ "--i": 7 } as CSSProperties}>
            <div className="border-b-2 border-(--tinta) px-4 py-3">
              <h2 className="font-titulo text-2xl">Actividad reciente</h2>
            </div>
            {data.recientes.length === 0 ? (
              <p className="px-4 py-8 text-center text-sm text-zinc-500">Aún no se han subido hojas de vida.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-[11px] uppercase italic tracking-wider text-zinc-500">
                    <tr><th className="px-4 py-2 font-extrabold">Candidato</th><th className="px-4 py-2 font-extrabold">Vacante</th>
                      <th className="px-4 py-2 font-extrabold">Resultado</th><th className="px-4 py-2 text-right font-extrabold">Fecha</th></tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                    {data.recientes.map((r, i) => (
                      <tr key={r.id} className="a-entra" style={{ "--i": i + 8 } as CSSProperties}>
                        <td className="px-4 py-2.5">
                          <p className="font-bold">{r.nombre || r.archivo}</p>
                          {r.nombre && <p className="text-xs text-zinc-500">{r.archivo}</p>}
                        </td>
                        <td className="max-w-56 truncate px-4 py-2.5 text-zinc-600 dark:text-zinc-400">
                          <Link to={`/app/vacantes/${r.vacante_id}/ranking`} className="hover:underline">{r.vacante.split("·")[0]}</Link>
                        </td>
                        <td className="px-4 py-2.5">
                          {r.estado === "evaluado" ? <span className="font-titulo text-xl">{fmt(r.puntaje ?? 0)} <span className="font-sans text-xs font-semibold text-zinc-500">pts</span></span>
                            : <Insignia tono="ambar"><Pencil className="size-3" /> Revisión manual</Insignia>}
                        </td>
                        <td className="whitespace-nowrap px-4 py-2.5 text-right text-xs text-zinc-500">{fechaCorta(r.creado)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      )}
    </>
  );
}
