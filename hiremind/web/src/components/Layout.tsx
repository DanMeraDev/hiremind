import { useQuery } from "@tanstack/react-query";
import clsx from "clsx";
import { Briefcase, ChevronRight, Cpu, FileUp, LayoutDashboard, ListChecks, Menu, Trophy, UserCheck, X } from "lucide-react";
import { useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router";
import { api } from "../api";
import { BotonTema, Logo } from "./ui";

function EstadoLLM() {
  const { data, isLoading } = useQuery({ queryKey: ["estado"], queryFn: api.estado, refetchInterval: 15000 });
  const ok = data?.llm_ok;
  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-3 text-xs dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center gap-2 font-medium">
        <span className="relative flex size-2">
          {ok && <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-60" />}
          <span className={clsx("relative inline-flex size-2 rounded-full", isLoading ? "bg-zinc-300" : ok ? "bg-emerald-500" : "bg-rose-500")} />
        </span>
        {isLoading ? "Comprobando modelo…" : ok ? "Modelo local activo" : "Modelo sin conexión"}
      </div>
      <div className="mt-1 flex items-center gap-1.5 truncate text-zinc-500" title={data?.mensaje}>
        <Cpu className="size-3.5 shrink-0" />
        <span className="truncate">{ok ? data?.modelo : data?.mensaje ?? "—"}</span>
      </div>
    </div>
  );
}

function Navegacion({ alNavegar }: { alNavegar?: () => void }) {
  const { data: vacantes } = useQuery({ queryKey: ["vacantes"], queryFn: api.vacantes });
  // el layout es padre de la ruta de la vacante: el id se lee de la URL
  const id = useLocation().pathname.match(/\/app\/vacantes\/(\d+)/)?.[1];
  const enlace = ({ isActive }: { isActive: boolean }) =>
    clsx(
      "flex items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-sm font-medium transition",
      isActive
        ? "bg-white text-zinc-900 shadow-xs ring-1 ring-zinc-200 dark:bg-zinc-800 dark:text-white dark:ring-zinc-700"
        : "text-zinc-600 hover:bg-zinc-200/60 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/70 dark:hover:text-zinc-100",
    );
  return (
    <nav className="flex flex-1 flex-col gap-6 overflow-y-auto" onClick={alNavegar}>
      <div className="space-y-0.5">
        <NavLink to="/app" end className={enlace}><LayoutDashboard className="size-4" /> Panel</NavLink>
        <NavLink to="/app/vacantes" end className={enlace}><Briefcase className="size-4" /> Vacantes</NavLink>
      </div>
      {!!vacantes?.length && (
        <div>
          <p className="mb-1.5 px-2.5 text-[11px] font-medium uppercase tracking-wider text-zinc-400">Procesos activos</p>
          <div className="space-y-0.5">
            {vacantes.map((v) => (
              <Link key={v.id} to={`/app/vacantes/${v.id}/ranking`}
                className={clsx(
                  "group flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-sm transition",
                  String(v.id) === id ? "bg-marca-50 text-marca-700 dark:bg-marca-950 dark:text-marca-300"
                    : "text-zinc-600 hover:bg-zinc-200/60 dark:text-zinc-400 dark:hover:bg-zinc-800/70",
                )}>
                <span className="truncate">{v.titulo.split("·")[0].trim()}</span>
                <span className="ml-auto rounded-md bg-zinc-200/70 px-1.5 text-[11px] tabular-nums text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">
                  {v.evaluados ?? 0}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}

function BarraLateral({ alNavegar }: { alNavegar?: () => void }) {
  return (
    <div className="flex h-full flex-col gap-6 p-4">
      <div className="flex items-center justify-between">
        <Link to="/" className="px-1"><Logo /></Link>
        <BotonTema />
      </div>
      <Navegacion alNavegar={alNavegar} />
      <div className="space-y-3">
        <EstadoLLM />
        <p className="flex gap-2 px-1 text-xs leading-relaxed text-zinc-500">
          <UserCheck className="mt-0.5 size-3.5 shrink-0" />
          <span>La IA ordena y justifica. <strong className="font-medium text-zinc-700 dark:text-zinc-300">La decisión final es de una persona.</strong></span>
        </p>
      </div>
    </div>
  );
}

export function AppLayout() {
  const [abierto, setAbierto] = useState(false);
  return (
    <div className="min-h-dvh lg:pl-64">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-zinc-200 bg-zinc-100/60 lg:block dark:border-zinc-800 dark:bg-zinc-900/40">
        <BarraLateral />
      </aside>

      {/* móvil */}
      <header className="sticky top-0 z-30 flex items-center justify-between border-b border-zinc-200 bg-white/80 px-4 py-2.5 backdrop-blur lg:hidden dark:border-zinc-800 dark:bg-zinc-950/80">
        <Link to="/"><Logo /></Link>
        <button className="btn-fantasma px-2" onClick={() => setAbierto(true)} aria-label="Abrir menú"><Menu className="size-5" /></button>
      </header>
      {abierto && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-zinc-950/40" onClick={() => setAbierto(false)} />
          <div className="absolute inset-y-0 left-0 w-72 bg-zinc-50 shadow-xl dark:bg-zinc-900">
            <button className="btn-fantasma absolute right-3 top-3 px-2" onClick={() => setAbierto(false)} aria-label="Cerrar menú"><X className="size-5" /></button>
            <BarraLateral alNavegar={() => setAbierto(false)} />
          </div>
        </div>
      )}

      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-8 sm:py-8">
        <Outlet />
      </main>
    </div>
  );
}

/** Pestañas de una vacante: los 3 pasos del proceso. */
export function PestanasVacante({ id, titulo, evaluados }: { id: number; titulo: string; evaluados?: number }) {
  const { pathname } = useLocation();
  const pasos = [
    { a: `/app/vacantes/${id}`, n: 1, texto: "Criterios", icono: ListChecks },
    { a: `/app/vacantes/${id}/cvs`, n: 2, texto: "Hojas de vida", icono: FileUp },
    { a: `/app/vacantes/${id}/ranking`, n: 3, texto: "Ranking", icono: Trophy },
  ];
  return (
    <div className="mb-6">
      <div className="mb-3 flex items-center gap-1.5 text-sm text-zinc-500">
        <Link to="/app/vacantes" className="hover:text-zinc-900 dark:hover:text-zinc-200">Vacantes</Link>
        <ChevronRight className="size-3.5" />
        <span className="truncate text-zinc-900 dark:text-zinc-200">{titulo}</span>
      </div>
      <div className="flex gap-1 overflow-x-auto border-b border-zinc-200 dark:border-zinc-800">
        {pasos.map((p) => {
          const activo = pathname === p.a;
          return (
            <Link key={p.a} to={p.a}
              className={clsx(
                "-mb-px flex shrink-0 items-center gap-2 border-b-2 px-3 py-2.5 text-sm font-medium transition",
                activo ? "border-marca-600 text-marca-700 dark:border-marca-400 dark:text-marca-300"
                  : "border-transparent text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200",
              )}>
              <span className={clsx("flex size-5 items-center justify-center rounded-full text-[11px]",
                activo ? "bg-marca-600 text-white" : "bg-zinc-200 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400")}>{p.n}</span>
              {p.texto}
              {p.n === 3 && !!evaluados && <span className="text-xs tabular-nums text-zinc-400">{evaluados}</span>}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
