import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Briefcase, Clock, FileText, Pencil, ScanLine, Sparkles, Trophy } from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "react-router";
import { api } from "../api";
import { BarraPuntaje, Cargando, Encabezado, Insignia, Vacio, fechaCorta, fmt } from "../components/ui";

function Kpi({ icono, etiqueta, valor, nota }: { icono: ReactNode; etiqueta: string; valor: ReactNode; nota?: string }) {
  return (
    <div className="tarjeta p-4">
      <div className="flex items-center justify-between text-sm text-zinc-500">
        {etiqueta}
        <span className="text-zinc-400">{icono}</span>
      </div>
      <div className="mt-2 text-2xl font-semibold tabular-nums tracking-tight">{valor}</div>
      {nota && <p className="mt-0.5 text-xs text-zinc-500">{nota}</p>}
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
            <Kpi icono={<Briefcase className="size-4" />} etiqueta="Vacantes" valor={data.vacantes} />
            <Kpi icono={<FileText className="size-4" />} etiqueta="CV evaluados" valor={data.evaluados}
              nota={data.corregidas ? `${data.corregidas} con corrección humana` : undefined} />
            <Kpi icono={<ScanLine className="size-4" />} etiqueta="Revisión manual" valor={data.revision} nota="Escaneados o ilegibles" />
            <Kpi icono={<Clock className="size-4" />} etiqueta="Tiempo por CV"
              valor={data.segundos_promedio != null ? `${fmt(data.segundos_promedio)} s` : "—"} nota="Promedio, en este equipo" />
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <section className="tarjeta lg:col-span-2">
              <div className="flex items-center justify-between border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
                <h2 className="text-sm font-semibold">Procesos de selección</h2>
                <Link to="/app/vacantes" className="text-xs font-medium text-marca-600 hover:underline dark:text-marca-400">Ver todas</Link>
              </div>
              <ul className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {data.por_vacante.map((v) => (
                  <li key={v.id} className="flex flex-col gap-3 px-4 py-3.5 sm:flex-row sm:items-center">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{v.titulo}</p>
                      <p className="mt-0.5 text-xs text-zinc-500">
                        {v.criterios.length} criterios · {v.evaluados ?? 0} evaluados
                        {!!v.revision && <> · <span className="text-amber-600 dark:text-amber-400">{v.revision} en revisión manual</span></>}
                      </p>
                    </div>
                    <div className="w-full sm:w-40">
                      {v.mejor != null ? (
                        <>
                          <div className="mb-1 flex justify-between text-xs text-zinc-500">
                            <span>Mejor puntaje</span><span className="font-medium tabular-nums text-zinc-900 dark:text-zinc-100">{fmt(v.mejor)}</span>
                          </div>
                          <BarraPuntaje puntaje={v.mejor} />
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

            <section className="tarjeta p-4">
              <h2 className="text-sm font-semibold">Distribución de puntajes</h2>
              <p className="mt-0.5 text-xs text-zinc-500">Todos los CV evaluados</p>
              <div className="mt-5 flex h-40 items-end gap-3">
                {data.distribucion.map((d) => (
                  <div key={d.rango} className="flex h-full flex-1 flex-col items-center justify-end gap-1.5">
                    <span className="text-xs font-medium tabular-nums">{d.cantidad}</span>
                    <div className="w-full rounded-t-md bg-marca-500/85 transition-all dark:bg-marca-400/80"
                      style={{ height: `${(d.cantidad / maxDist) * 100}%`, minHeight: d.cantidad ? 4 : 2 }} />
                    <span className="text-[11px] tabular-nums text-zinc-500">{d.rango}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <section className="tarjeta">
            <div className="border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
              <h2 className="text-sm font-semibold">Actividad reciente</h2>
            </div>
            {data.recientes.length === 0 ? (
              <p className="px-4 py-8 text-center text-sm text-zinc-500">Aún no se han subido hojas de vida.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-xs text-zinc-500">
                    <tr><th className="px-4 py-2 font-medium">Candidato</th><th className="px-4 py-2 font-medium">Vacante</th>
                      <th className="px-4 py-2 font-medium">Resultado</th><th className="px-4 py-2 text-right font-medium">Fecha</th></tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                    {data.recientes.map((r) => (
                      <tr key={r.id}>
                        <td className="px-4 py-2.5">
                          <p className="font-medium">{r.nombre || r.archivo}</p>
                          {r.nombre && <p className="text-xs text-zinc-500">{r.archivo}</p>}
                        </td>
                        <td className="max-w-56 truncate px-4 py-2.5 text-zinc-600 dark:text-zinc-400">
                          <Link to={`/app/vacantes/${r.vacante_id}/ranking`} className="hover:underline">{r.vacante.split("·")[0]}</Link>
                        </td>
                        <td className="px-4 py-2.5">
                          {r.estado === "evaluado" ? <span className="font-medium tabular-nums">{fmt(r.puntaje ?? 0)} pts</span>
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
