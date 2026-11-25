import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { Briefcase, ChevronRight, Cpu, FileUp, LayoutDashboard, ListChecks, LogOut, Menu, Trophy, UserCheck, UserRound, X } from "lucide-react";
import { useState, type CSSProperties } from "react";
import { Palabras } from "./anim";
import { Link, Navigate, NavLink, Outlet, useLocation, useNavigate } from "react-router";
import { api, ErrorApi } from "../api";
import { BotonTema, Cargando, Logo } from "./ui";

function EstadoLLM() {
  const { data, isLoading } = useQuery({ queryKey: ["estado"], queryFn: api.estado, refetchInterval: 15000 });
  const ok = data?.llm_ok;
  return (
    <div className={clsx("border-2 border-(--tinta) p-3 text-xs shadow-xs", ok ? "bg-menta-claro dark:bg-zinc-900" : "bg-white dark:bg-zinc-900")}>
      <div className="flex items-center gap-2 font-bold">
        <span className="relative flex size-2.5">
          {ok && <span className="absolute inline-flex size-full animate-[hm-late_1.6s_ease-out_infinite] bg-menta" />}
          <span className={clsx("relative inline-flex size-2.5 border-[1.5px] border-noche", isLoading ? "bg-zinc-300" : ok ? "bg-menta" : "bg-coral")} />
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
      "flex items-center gap-2.5 border-2 px-2.5 py-1.5 text-sm font-bold transition-[transform,background-color,box-shadow] duration-200 ease-rebote",
      isActive
        ? "border-(--tinta) bg-menta text-noche shadow-xs"
        : "border-transparent text-zinc-600 hover:translate-x-1 hover:bg-zinc-100 hover:text-noche dark:text-zinc-300 dark:hover:bg-zinc-800 dark:hover:text-white",
    );
  return (
    <nav className="flex flex-1 flex-col gap-6 overflow-y-auto" onClick={alNavegar}>
      <div className="space-y-0.5">
        <NavLink to="/app" end className={enlace}><LayoutDashboard className="size-4" /> Panel</NavLink>
        <NavLink to="/app/vacantes" end className={enlace}><Briefcase className="size-4" /> Vacantes</NavLink>
      </div>
      {!!vacantes?.length && (
        <div>
          <p className="mb-1.5 px-2.5 text-[11px] font-extrabold uppercase italic tracking-wider text-zinc-500">Procesos activos</p>
          <div className="space-y-0.5">
            {vacantes.map((v, i) => (
              <Link key={v.id} style={{ "--i": i } as CSSProperties} to={`/app/vacantes/${v.id}/ranking`}
                className={clsx(
                  "a-entra group flex items-center gap-2 border-l-4 px-2.5 py-1.5 text-sm font-medium transition-colors",
                  String(v.id) === id ? "border-coral bg-azul-claro font-bold text-noche dark:bg-marca-950 dark:text-white"
                    : "border-transparent text-zinc-600 hover:border-zinc-300 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800",
                )}>
                <span className="truncate">{v.titulo.split("·")[0].trim()}</span>
                <span className="ml-auto border-[1.5px] border-(--tinta) bg-white px-1.5 text-[11px] font-bold tabular-nums text-noche dark:bg-zinc-950 dark:text-zinc-200">
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

function Cuenta() {
  const { data: u } = useQuery({ queryKey: ["yo"], queryFn: api.yo });
  const qc = useQueryClient();
  const navegar = useNavigate();
  const salir = useMutation({
    mutationFn: api.logout,
    onSettled: () => {
      qc.clear();
      navegar("/login", { replace: true });
    },
  });
  if (!u) return null;
  return (
    <div className="flex items-center gap-2.5 border-2 border-(--tinta) bg-white p-2.5 shadow-xs dark:bg-zinc-900">
      <span className="flex size-8 shrink-0 items-center justify-center border-2 border-(--tinta) bg-ambar text-noche">
        <UserRound className="size-4" />
      </span>
      <div className="min-w-0 flex-1 leading-tight">
        <p className="truncate text-sm font-bold">{u.nombre}</p>
        <p className="truncate text-xs text-zinc-500">{u.usuario}</p>
      </div>
      <button className="btn-fantasma px-2" onClick={() => salir.mutate()} disabled={salir.isPending}
        title="Cerrar sesión" aria-label="Cerrar sesión">
        <LogOut className="size-4" />
      </button>
    </div>
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
        <Cuenta />
        <EstadoLLM />
        <p className="flex gap-2 px-1 text-xs font-medium leading-relaxed text-zinc-500">
          <UserCheck className="mt-0.5 size-3.5 shrink-0" />
          <span>La IA ordena y justifica. <strong className="font-bold text-noche dark:text-zinc-100">La decisión final es de una persona.</strong></span>
        </p>
      </div>
    </div>
  );
}

export function AppLayout() {
  const [abierto, setAbierto] = useState(false);
  const { pathname } = useLocation();
  const yo = useQuery({ queryKey: ["yo"], queryFn: api.yo, retry: false, staleTime: 60_000 });
  if (yo.isLoading) return <div className="flex min-h-dvh items-center justify-center"><Cargando texto="Comprobando sesión…" /></div>;
  if (yo.error instanceof ErrorApi && yo.error.status === 401)
    return <Navigate to={`/login?volver=${encodeURIComponent(pathname)}`} replace />;
  return (
    <div className="relative min-h-dvh lg:pl-64">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r-2 border-(--tinta) bg-white lg:block dark:bg-zinc-900">
        <BarraLateral />
      </aside>

      {/* móvil */}
      <header className="sticky top-0 z-30 flex items-center justify-between border-b-2 border-(--tinta) bg-white px-4 py-2.5 lg:hidden dark:bg-zinc-900">
        <Link to="/"><Logo /></Link>
        <button className="btn-fantasma px-2" onClick={() => setAbierto(true)} aria-label="Abrir menú"><Menu className="size-5" /></button>
      </header>
      {abierto && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 animate-[hm-sube_.2s_ease-out_both] bg-noche/50" onClick={() => setAbierto(false)} />
          <div className="a-entra absolute inset-y-0 left-0 w-72 border-r-2 border-(--tinta) bg-white shadow-xl dark:bg-zinc-900">
            <button className="btn-fantasma absolute right-3 top-3 px-2" onClick={() => setAbierto(false)} aria-label="Cerrar menú"><X className="size-5" /></button>
            <BarraLateral alNavegar={() => setAbierto(false)} />
          </div>
        </div>
      )}

      {/* franja azul y bloque coral: la firma geométrica de la marca */}
      <span aria-hidden className="pointer-events-none absolute right-6 top-0 hidden h-3 w-44 bg-azul sm:block lg:right-16" />
      <span aria-hidden className="pointer-events-none fixed -bottom-10 -right-10 hidden size-28 rounded-full border-[14px] border-coral/80 xl:block" />
      <main className="relative mx-auto max-w-6xl px-4 py-6 sm:px-8 sm:py-10">
        <div key={pathname} className="a-sube">
          <Outlet />
        </div>
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
      <div className="mb-2 flex items-center gap-1.5 text-sm font-medium text-zinc-500">
        <Link to="/app/vacantes" className="hover:text-zinc-900 dark:hover:text-zinc-200">Vacantes</Link>
        <ChevronRight className="size-3.5" />
        <span className="truncate text-noche dark:text-zinc-200">{titulo.split("·")[1]?.trim()}</span>
      </div>
      <Palabras como="h1" texto={titulo.split("·")[0].trim().toUpperCase()} className="mb-4 font-titulo text-5xl" />
      <div className="flex gap-2 overflow-x-auto overflow-y-hidden shadow-[inset_0_-2px_0_0_var(--tinta)]">
        {pasos.map((p) => {
          const activo = pathname === p.a;
          return (
            <Link key={p.a} to={p.a}
              className={clsx(
                "flex shrink-0 items-center gap-2 border-b-[5px] px-3 py-2.5 text-sm font-extrabold uppercase tracking-wide transition-colors",
                activo ? "border-coral text-noche dark:text-white"
                  : "border-transparent text-zinc-500 hover:border-zinc-300 hover:text-noche dark:hover:text-white",
              )}>
              <span className={clsx("flex size-6 items-center justify-center border-2 font-titulo text-base transition-colors",
                activo ? "border-(--tinta) bg-coral text-noche shadow-xs" : "border-zinc-300 text-zinc-500 dark:border-zinc-600")}>{p.n}</span>
              {p.texto}
              {p.n === 3 && !!evaluados && <span className="text-xs tabular-nums text-zinc-400">{evaluados}</span>}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
