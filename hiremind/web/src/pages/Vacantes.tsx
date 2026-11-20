import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Briefcase, FileUp, Plus, Sparkles, Trophy } from "lucide-react";
import clsx from "clsx";
import type { CSSProperties } from "react";
import { Link } from "react-router";
import { api, NOMBRE_TIPO } from "../api";
import { BarraPuntaje, Cargando, Encabezado, Insignia, Vacio, fmt } from "../components/ui";

export default function Vacantes() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["vacantes"], queryFn: api.vacantes });
  const demo = useMutation({ mutationFn: api.cargarDemo, onSuccess: () => qc.invalidateQueries() });

  if (isLoading || !data) return <Cargando />;
  return (
    <>
      <Encabezado
        titulo="Vacantes"
        descripcion="Cada vacante define qué se busca y cuánto pesa cada criterio."
        acciones={
          <>
            <button className="btn-secundario" onClick={() => demo.mutate()} disabled={demo.isPending}>
              <Sparkles className="size-4" /> Ejemplos
            </button>
            <Link to="/app/vacantes/nueva" className="btn-primario"><Plus className="size-4" /> Nueva vacante</Link>
          </>
        }
      />
      {data.length === 0 ? (
        <Vacio icono={<Briefcase className="size-5" />} titulo="Sin vacantes"
          texto="Cree la primera vacante o cargue los ejemplos (asistente contable y desarrollador/a junior)." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {data.map((v, i) => {
            const [puesto, empresa] = v.titulo.split("·").map((s) => s.trim());
            return (
              <article key={v.id} style={{ "--i": i } as CSSProperties}
                className="tarjeta a-sube relative flex flex-col p-5 pt-6 transition-[transform,box-shadow] duration-200 ease-rebote hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-md">
                <span aria-hidden className={clsx("absolute right-5 top-0 h-2 w-20", ["bg-azul", "bg-coral", "bg-menta"][i % 3])} />
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <Link to={`/app/vacantes/${v.id}`} className="font-titulo text-3xl hover:text-coral">{puesto}</Link>
                    {empresa && <p className="text-sm font-semibold text-zinc-500">{empresa}</p>}
                  </div>
                  {!!v.revision && <Insignia tono="ambar">{v.revision} manual</Insignia>}
                </div>
                {v.descripcion && <p className="mt-3 line-clamp-2 text-sm text-zinc-600 dark:text-zinc-400">{v.descripcion}</p>}
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {v.criterios.map((c) => (
                    <Insignia key={c.id} tono="neutro" className="font-normal">
                      <span className="font-extrabold uppercase text-zinc-400">{NOMBRE_TIPO[c.tipo]}</span> {c.nombre.replace(/\s*\(.*\)$/, "")}
                      <span className="font-bold tabular-nums text-noche dark:text-zinc-100">{c.peso}%</span>
                    </Insignia>
                  ))}
                </div>
                <div className="mt-5 flex items-end gap-3 border-t-2 border-zinc-100 pt-4 dark:border-zinc-800">
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-zinc-500">{v.evaluados ?? 0} CV evaluados{v.mejor != null && <> · mejor {fmt(v.mejor)}</>}</p>
                    {v.mejor != null && <BarraPuntaje puntaje={v.mejor} className="mt-1.5" i={i} />}
                  </div>
                  <Link to={`/app/vacantes/${v.id}/cvs`} className="btn-secundario py-1.5 text-xs"><FileUp className="size-3.5" /> Subir</Link>
                  <Link to={`/app/vacantes/${v.id}/ranking`} className="btn-primario py-1.5 text-xs"><Trophy className="size-3.5" /> Ranking</Link>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </>
  );
}
