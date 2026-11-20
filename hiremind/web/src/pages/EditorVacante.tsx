import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { Check, Plus, ShieldCheck, Trash2, X } from "lucide-react";
import { useEffect, useState, type KeyboardEvent } from "react";
import { useNavigate, useParams } from "react-router";
import {
  api, ErrorApi, NOMBRE_IDIOMA, NOMBRE_NIVEL, NOMBRE_TIPO,
  type Criterio, type NivelFormacion, type NivelIdioma, type TipoCriterio, type Vacante,
} from "../api";
import { PestanasVacante } from "../components/Layout";
import { Aviso, Cargando, Encabezado } from "../components/ui";

const nuevoCriterio = (): Criterio => ({
  id: `c${Date.now().toString(36)}`, tipo: "habilidad", nombre: "", peso: 10, palabras_clave: [],
  anios_min: 0, nivel_min: null, idioma: null, nivel_idioma: null,
});

const VACIA: Vacante = { id: null, titulo: "", descripcion: "", criterios: [nuevoCriterio()] };

function Palabras({ valor, onChange }: { valor: string[]; onChange: (v: string[]) => void }) {
  const [texto, setTexto] = useState("");
  const agregar = () => {
    const t = texto.trim().replace(/,$/, "");
    if (t && !valor.includes(t)) onChange([...valor, t]);
    setTexto("");
  };
  const tecla = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") { e.preventDefault(); agregar(); }
    if (e.key === "Backspace" && !texto && valor.length) onChange(valor.slice(0, -1));
  };
  return (
    <div className="campo flex min-h-10 flex-wrap items-center gap-1.5 py-1.5">
      {valor.map((p) => (
        <span key={p} className="inline-flex items-center gap-1 rounded-md bg-marca-50 py-0.5 pl-2 pr-1 text-xs font-medium text-marca-700 dark:bg-marca-950 dark:text-marca-300">
          {p}
          <button type="button" onClick={() => onChange(valor.filter((x) => x !== p))} aria-label={`Quitar ${p}`}
            className="rounded p-0.5 hover:bg-marca-100 dark:hover:bg-marca-900"><X className="size-3" /></button>
        </span>
      ))}
      <input value={texto} onChange={(e) => setTexto(e.target.value)} onKeyDown={tecla} onBlur={agregar}
        placeholder={valor.length ? "" : "Escriba y pulse Enter"} className="min-w-28 flex-1 bg-transparent text-sm outline-none placeholder:text-zinc-400" />
    </div>
  );
}

function TarjetaCriterio({ c, onChange, onBorrar, puedeBorrar }: {
  c: Criterio; onChange: (c: Criterio) => void; onBorrar: () => void; puedeBorrar: boolean;
}) {
  const set = <K extends keyof Criterio>(k: K, v: Criterio[K]) => onChange({ ...c, [k]: v });
  const cambiarTipo = (tipo: TipoCriterio) => onChange({
    ...c, tipo,
    anios_min: tipo === "experiencia" ? c.anios_min || 1 : 0,
    nivel_min: tipo === "formacion" ? c.nivel_min ?? "tercer_nivel" : null,
    idioma: tipo === "idioma" ? c.idioma ?? "ingles" : null,
    nivel_idioma: tipo === "idioma" ? c.nivel_idioma ?? "intermedio" : null,
  });
  return (
    <div className="tarjeta p-4">
      <div className="grid gap-3 sm:grid-cols-12">
        <div className="sm:col-span-3">
          <label className="etiqueta">Tipo</label>
          <select className="campo" value={c.tipo} onChange={(e) => cambiarTipo(e.target.value as TipoCriterio)}>
            {Object.entries(NOMBRE_TIPO).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </div>
        <div className="sm:col-span-6">
          <label className="etiqueta">Nombre del criterio</label>
          <input className="campo" value={c.nombre} onChange={(e) => set("nombre", e.target.value)} placeholder="Ej.: Excel avanzado" />
        </div>
        <div className="sm:col-span-3">
          <label className="etiqueta">Peso</label>
          <div className="relative">
            <input type="number" min={1} max={100} className="campo pr-8 tabular-nums" value={c.peso}
              onChange={(e) => set("peso", Number(e.target.value))} />
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-sm text-zinc-400">%</span>
          </div>
        </div>

        {c.tipo === "experiencia" && (
          <div className="sm:col-span-3">
            <label className="etiqueta">Años mínimos</label>
            <input type="number" min={0.5} step={0.5} className="campo" value={c.anios_min} onChange={(e) => set("anios_min", Number(e.target.value))} />
          </div>
        )}
        {c.tipo === "formacion" && (
          <div className="sm:col-span-3">
            <label className="etiqueta">Nivel mínimo</label>
            <select className="campo" value={c.nivel_min ?? ""} onChange={(e) => set("nivel_min", e.target.value as NivelFormacion)}>
              {Object.entries(NOMBRE_NIVEL).filter(([k]) => k !== "otro").map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
        )}
        {c.tipo === "idioma" && (
          <>
            <div className="sm:col-span-3">
              <label className="etiqueta">Idioma</label>
              <input className="campo" value={c.idioma ?? ""} onChange={(e) => set("idioma", e.target.value)} placeholder="ingles" />
            </div>
            <div className="sm:col-span-3">
              <label className="etiqueta">Nivel mínimo</label>
              <select className="campo" value={c.nivel_idioma ?? ""} onChange={(e) => set("nivel_idioma", e.target.value as NivelIdioma)}>
                {Object.entries(NOMBRE_IDIOMA).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
          </>
        )}
        <div className={c.tipo === "habilidad" ? "sm:col-span-12" : c.tipo === "idioma" ? "sm:col-span-6" : "sm:col-span-9"}>
          <label className="etiqueta">
            {c.tipo === "formacion" ? "Áreas aceptadas" : c.tipo === "idioma" ? "Otros nombres del idioma" : "Palabras clave y sinónimos"}
          </label>
          <Palabras valor={c.palabras_clave} onChange={(v) => set("palabras_clave", v)} />
        </div>
      </div>
      {puedeBorrar && (
        <div className="mt-3 flex justify-end">
          <button type="button" onClick={onBorrar} className="btn-fantasma py-1 text-xs text-rose-600 hover:bg-rose-50 hover:text-rose-700 dark:text-rose-400 dark:hover:bg-rose-950/50">
            <Trash2 className="size-3.5" /> Quitar criterio
          </button>
        </div>
      )}
    </div>
  );
}

export default function EditorVacante() {
  const { id } = useParams();
  const vid = id ? Number(id) : null;
  const nav = useNavigate();
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["vacante", vid], queryFn: () => api.vacante(vid!), enabled: vid != null });
  const [v, setV] = useState<Vacante>(VACIA);
  const [errores, setErrores] = useState<string[]>([]);
  const [guardado, setGuardado] = useState(false);

  useEffect(() => { setV(data ?? VACIA); setErrores([]); }, [data, vid]);

  const guardar = useMutation({
    mutationFn: api.guardarVacante,
    onSuccess: (r) => {
      setErrores([]);
      qc.invalidateQueries();
      if (!vid) nav(`/app/vacantes/${r.id}/cvs`);
      else { setGuardado(true); setTimeout(() => setGuardado(false), 2000); }
    },
    onError: (e) => setErrores(e instanceof ErrorApi ? e.errores : [String(e)]),
  });
  const borrar = useMutation({
    mutationFn: () => api.borrarVacante(vid!),
    onSuccess: () => { qc.invalidateQueries(); nav("/app/vacantes"); },
  });

  if (vid != null && (isLoading || !data)) return <Cargando />;
  const total = v.criterios.reduce((s, c) => s + (Number(c.peso) || 0), 0);
  const setCriterio = (i: number, c: Criterio) => setV({ ...v, criterios: v.criterios.map((x, j) => (j === i ? c : x)) });

  return (
    <>
      {vid != null
        ? <PestanasVacante id={vid} titulo={data!.titulo} evaluados={data!.evaluados} />
        : <Encabezado titulo="Nueva vacante" descripcion="Defina qué busca y cuánto pesa cada criterio. Luego podrá subir las hojas de vida." />}

      <form className="grid gap-6 lg:grid-cols-[1fr_280px]" onSubmit={(e) => { e.preventDefault(); guardar.mutate(v); }}>
        <div className="space-y-6">
          <section className="tarjeta space-y-4 p-5">
            <div>
              <label className="etiqueta">Título del puesto</label>
              <input className="campo" value={v.titulo} onChange={(e) => setV({ ...v, titulo: e.target.value })}
                placeholder="Asistente contable · Ferretería El Constructor (Quito)" required />
            </div>
            <div>
              <label className="etiqueta">Descripción</label>
              <textarea className="campo min-h-20" value={v.descripcion} onChange={(e) => setV({ ...v, descripcion: e.target.value })}
                placeholder="Funciones principales del puesto" />
            </div>
          </section>

          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold">Criterios de evaluación</h2>
              <button type="button" className="btn-secundario py-1.5 text-xs" onClick={() => setV({ ...v, criterios: [...v.criterios, nuevoCriterio()] })}>
                <Plus className="size-3.5" /> Agregar criterio
              </button>
            </div>
            {v.criterios.map((c, i) => (
              <TarjetaCriterio key={c.id} c={c} onChange={(n) => setCriterio(i, n)} puedeBorrar={v.criterios.length > 1}
                onBorrar={() => setV({ ...v, criterios: v.criterios.filter((_, j) => j !== i) })} />
            ))}
          </section>
        </div>

        <aside className="space-y-4 lg:sticky lg:top-8 lg:self-start">
          <div className="tarjeta p-4">
            <div className="flex items-baseline justify-between">
              <span className="text-sm font-medium">Suma de pesos</span>
              <span className={clsx("text-lg font-semibold tabular-nums", total === 100 ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400")}>
                {total} %
              </span>
            </div>
            <div className="mt-3 flex h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
              {v.criterios.map((c, i) => (
                <div key={c.id} title={`${c.nombre || "Sin nombre"}: ${c.peso}%`} style={{ width: `${Math.min(c.peso, 100)}%` }}
                  className={clsx("h-full border-r border-white last:border-0 dark:border-zinc-900", ["bg-marca-600", "bg-marca-400", "bg-sky-500", "bg-teal-500", "bg-violet-500", "bg-marca-300"][i % 6])} />
              ))}
            </div>
            <p className="mt-2 text-xs text-zinc-500">{total === 100 ? "Los pesos están completos." : `Deben sumar 100 % (faltan ${100 - total}).`}</p>
            <p className="mt-3 border-t border-zinc-100 pt-3 text-xs text-zinc-500 dark:border-zinc-800">
              Puntaje = Σ peso × resultado. Cumple vale 1, parcial 0,5 y no identificado 0.
            </p>
          </div>

          <Aviso tono="marca">
            <div className="flex gap-2">
              <ShieldCheck className="mt-0.5 size-4 shrink-0" />
              <span>No se aceptan criterios sobre edad, género, estado civil, nacionalidad o religión.</span>
            </div>
          </Aviso>

          {errores.length > 0 && (
            <Aviso>
              <ul className="list-disc space-y-1 pl-4">{errores.map((e) => <li key={e}>{e}</li>)}</ul>
            </Aviso>
          )}

          <div className="flex flex-col gap-2">
            <button type="submit" className="btn-primario w-full" disabled={guardar.isPending}>
              {guardado ? <><Check className="size-4" /> Guardado</> : vid ? "Guardar cambios" : "Crear y subir hojas de vida"}
            </button>
            {vid != null && (
              <button type="button" className="btn-fantasma w-full text-rose-600 dark:text-rose-400"
                onClick={() => confirm("¿Eliminar la vacante y todas sus evaluaciones?") && borrar.mutate()}>
                <Trash2 className="size-4" /> Eliminar vacante
              </button>
            )}
          </div>
        </aside>
      </form>
    </>
  );
}
