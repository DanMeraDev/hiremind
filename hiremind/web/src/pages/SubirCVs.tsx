import { useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { ArrowRight, CircleCheck, EyeOff, FileText, FileUp, LoaderCircle, Lock, ScanLine, TriangleAlert, X } from "lucide-react";
import { useRef, useState, type CSSProperties, type DragEvent } from "react";
import { Cifra } from "../components/anim";
import { Link, useParams } from "react-router";
import { api, ErrorApi, type ResultadoCV } from "../api";
import { PestanasVacante } from "../components/Layout";
import { Aviso, BarraPuntaje, Cargando, Insignia, fmt } from "../components/ui";

type Fila = { archivo: File; estado: "pendiente" | "procesando" | "listo" | "error"; resultado?: ResultadoCV; error?: string };

export default function SubirCVs() {
  const vid = Number(useParams().id);
  const qc = useQueryClient();
  const { data: vac, isLoading } = useQuery({ queryKey: ["vacante", vid], queryFn: () => api.vacante(vid) });
  const { data: estado } = useQuery({ queryKey: ["estado"], queryFn: api.estado });
  const [filas, setFilas] = useState<Fila[]>([]);
  const [arrastrando, setArrastrando] = useState(false);
  const [trabajando, setTrabajando] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  const agregar = (lista: FileList | null) => {
    if (!lista || trabajando) return; // no cambiar la lista mientras se evalúa
    const nuevos = [...lista].filter((f) => f.name.toLowerCase().endsWith(".pdf") && !filas.some((x) => x.archivo.name === f.name));
    setFilas((fs) => [...fs.filter((x) => x.estado !== "listo"), ...nuevos.map((archivo) => ({ archivo, estado: "pendiente" as const }))]);
  };
  const soltar = (e: DragEvent) => { e.preventDefault(); setArrastrando(false); agregar(e.dataTransfer.files); };

  const evaluar = async () => {
    setTrabajando(true);
    for (let i = 0; i < filas.length; i++) {
      if (filas[i].estado !== "pendiente") continue;
      setFilas((fs) => fs.map((f, j) => (j === i ? { ...f, estado: "procesando" } : f)));
      try {
        const r = await api.subirCV(vid, filas[i].archivo);
        setFilas((fs) => fs.map((f, j) => (j === i ? { ...f, estado: "listo", resultado: r } : f)));
      } catch (e) {
        const msg = e instanceof ErrorApi ? e.message : String(e);
        setFilas((fs) => fs.map((f, j) => (j === i ? { ...f, estado: "error", error: msg } : f)));
      }
    }
    setTrabajando(false);
    qc.invalidateQueries();
  };

  if (isLoading || !vac) return <Cargando />;
  const pendientes = filas.filter((f) => f.estado === "pendiente").length;
  const listos = filas.filter((f) => f.estado === "listo");
  const hechos = filas.filter((f) => f.estado === "listo" || f.estado === "error").length;
  const tiempos = listos.filter((f) => f.resultado?.estado === "evaluado").map((f) => f.resultado!.segundos);
  const promedio = tiempos.length ? tiempos.reduce((a, b) => a + b, 0) / tiempos.length : null;
  const llmOk = estado?.llm_ok ?? false;

  return (
    <>
      <PestanasVacante id={vid} titulo={vac.titulo} evaluados={vac.evaluados} />

      <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <div className="space-y-4">
          <div
            onDragOver={(e) => { e.preventDefault(); setArrastrando(true); }}
            onDragLeave={() => setArrastrando(false)}
            onDrop={soltar}
            onClick={() => input.current?.click()}
            className={clsx(
              "group relative flex cursor-pointer flex-col items-center justify-center overflow-hidden border-[3px] border-dashed border-(--tinta) px-6 py-14 text-center transition-[background-color,transform,box-shadow] duration-200 ease-rebote",
              arrastrando ? "scale-[1.01] border-solid bg-menta-claro shadow-md dark:bg-marca-950" : "bg-white hover:bg-menta-claro/60 dark:bg-zinc-900 dark:hover:bg-zinc-800",
            )}>
            <span aria-hidden className="absolute -right-5 -top-5 size-14 rounded-full border-[9px] border-coral" />
            <span aria-hidden className="absolute bottom-0 left-8 h-2 w-24 bg-azul" />
            <div className={clsx("mb-4 flex size-14 items-center justify-center border-2 border-(--tinta) bg-menta text-noche shadow-xs transition-transform duration-300 ease-rebote group-hover:-translate-y-1 group-hover:rotate-3", arrastrando && "-translate-y-2 rotate-6")}>
              <FileUp className="size-7" />
            </div>
            <p className="font-titulo text-3xl">{arrastrando ? "Suéltelas aquí" : "Arrastre las hojas de vida aquí"}</p>
            <p className="mt-1 text-sm font-medium text-zinc-500">o haga clic para elegirlas · solo PDF</p>
            <input ref={input} type="file" accept="application/pdf,.pdf" multiple hidden onChange={(e) => { agregar(e.target.files); e.target.value = ""; }} />
          </div>

          {!llmOk && <Aviso tono="ambar">El modelo local no responde ({estado?.mensaje ?? "comprobando…"}). Encienda LM Studio para evaluar.</Aviso>}

          {filas.length > 0 && (
            <section className="tarjeta">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b-2 border-(--tinta) px-4 py-3">
                <div className="flex items-baseline gap-2">
                  <span className="font-titulo text-2xl">{filas.length} archivos</span>
                  {trabajando && <span className="text-sm font-semibold text-zinc-500">procesando {hechos + 1} de {filas.length}</span>}
                </div>
                <div className="flex gap-2">
                  {!trabajando && pendientes > 0 && (
                    <button className="btn-fantasma py-1.5 text-xs" onClick={() => setFilas((fs) => fs.filter((f) => f.estado !== "pendiente"))}>Quitar pendientes</button>
                  )}
                  <button className="btn-primario py-1.5 text-xs" onClick={evaluar} disabled={trabajando || !pendientes || !llmOk}>
                    {trabajando ? <><LoaderCircle className="size-3.5 animate-spin" /> Evaluando {hechos + 1} de {filas.length}…</> : <>Evaluar {pendientes || ""} <ArrowRight className="flecha size-3.5" /></>}
                  </button>
                </div>
              </div>
              {trabajando && (
                <div className="h-3 border-b-2 border-(--tinta) bg-azul-claro dark:bg-zinc-800">
                  <div className="h-full border-r-2 border-(--tinta) bg-menta transition-[width] duration-700 ease-rebote" style={{ width: `${Math.max(2, (hechos / filas.length) * 100)}%` }} />
                </div>
              )}
              <ul className="divide-y-2 divide-zinc-100 dark:divide-zinc-800">
                {filas.map((f, i) => {
                  const r = f.resultado;
                  return (
                    <li key={f.archivo.name} style={{ "--i": i } as CSSProperties}
                      className={clsx("a-entra flex items-center gap-3 px-4 py-3 transition-colors", f.estado === "procesando" && "bg-azul-claro dark:bg-marca-950")}>
                      <div key={f.estado} className={clsx("flex size-10 shrink-0 items-center justify-center border-2 border-(--tinta)",
                        f.estado === "procesando" ? "escaneo bg-white text-noche" : "a-pop",
                        r?.estado === "revision_manual" || f.estado === "error" ? "bg-ambar text-noche"
                          : r ? "bg-menta text-noche" : f.estado !== "procesando" && "bg-white text-zinc-500 dark:bg-zinc-900")}>
                        {f.estado === "procesando" ? <FileText className="size-5" />
                          : r?.estado === "revision_manual" ? <ScanLine className="size-4" />
                          : f.estado === "error" ? <TriangleAlert className="size-4" />
                          : r ? <CircleCheck className="size-4" /> : <FileText className="size-4" />}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-bold">{r?.nombre || f.archivo.name}</p>
                        <p className="truncate text-xs font-medium text-zinc-500">
                          {f.estado === "pendiente" && `${f.archivo.name} · ${(f.archivo.size / 1024).toFixed(0)} KB`}
                          {f.estado === "procesando" && "Leyendo, extrayendo y verificando citas…"}
                          {f.estado === "error" && f.error}
                          {r?.estado === "revision_manual" && r.motivo}
                          {r?.estado === "evaluado" && (
                            <>
                              {f.archivo.name} · {fmt(r.segundos)} s
                              {r.datos_quitados.length > 0 && <> · <EyeOff className="inline size-3" /> {r.datos_quitados.length} datos personales excluidos</>}
                            </>
                          )}
                        </p>
                      </div>
                      {r?.estado === "evaluado" && (
                        <div className="a-pop w-28 shrink-0 text-right">
                          <span className="font-titulo text-2xl leading-none"><Cifra valor={r.puntaje} /></span>
                          <BarraPuntaje puntaje={r.puntaje} className="mt-1" />
                        </div>
                      )}
                      {r?.estado === "revision_manual" && <Insignia tono="ambar">Revisión manual</Insignia>}
                      {f.estado === "pendiente" && !trabajando && (
                        <button className="btn-fantasma px-1.5" aria-label="Quitar" onClick={() => setFilas((fs) => fs.filter((_, j) => j !== i))}>
                          <X className="size-4" />
                        </button>
                      )}
                    </li>
                  );
                })}
              </ul>
            </section>
          )}
        </div>

        <aside className="space-y-4 lg:sticky lg:top-8 lg:self-start">
          <div className="tarjeta p-4">
            <h3 className="font-titulo text-2xl">Qué pasa con cada CV</h3>
            <ol className="mt-3 space-y-2.5 text-xs font-medium text-zinc-600 dark:text-zinc-300">
              {[
                "Se lee el PDF. Si es escaneado, va a revisión manual.",
                "Se quitan edad, estado civil, nacionalidad y otros datos personales.",
                "El modelo extrae los datos con una cita textual del CV.",
                "Python verifica cada cita y calcula el puntaje.",
              ].map((t, i) => (
                <li key={t} className="a-entra flex gap-2.5" style={{ "--i": i + 2 } as CSSProperties}>
                  <span className={clsx("flex size-6 shrink-0 items-center justify-center border-2 border-(--tinta) font-titulo text-base text-noche", ["bg-menta", "bg-coral", "bg-azul", "bg-ambar"][i])}>{i + 1}</span>
                  {t}
                </li>
              ))}
            </ol>
            <p className="mt-4 flex items-center gap-1.5 border-t-2 border-zinc-100 pt-3 text-xs font-semibold text-zinc-500 dark:border-zinc-800">
              <Lock className="size-3.5" /> Los archivos no salen de este equipo.
            </p>
          </div>

          {listos.length > 0 && !trabajando && (
            <div className="tarjeta a-pop bg-menta-claro p-4 dark:bg-zinc-900">
              <p className="font-titulo text-3xl"><Cifra valor={listos.length} /> procesados</p>
              {promedio != null && <p className="mt-0.5 text-xs text-zinc-500">Promedio {fmt(Math.round(promedio * 10) / 10)} s por CV</p>}
              <Link to={`/app/vacantes/${vid}/ranking`} className="btn-primario mt-3 w-full">Ver ranking <ArrowRight className="flecha size-4" /></Link>
            </div>
          )}
        </aside>
      </div>
    </>
  );
}
