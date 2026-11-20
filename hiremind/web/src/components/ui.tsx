import clsx from "clsx";
import { CircleCheck, CircleDashed, CircleMinus, LoaderCircle, Moon, Sun } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { NOMBRE_ESTADO, type Estado } from "../api";

export function Logo({ className }: { className?: string }) {
  return (
    <span className={clsx("flex items-center gap-2 font-semibold tracking-tight", className)}>
      <svg viewBox="0 0 32 32" className="size-7 shrink-0" aria-hidden>
        <rect width="32" height="32" rx="8" className="fill-marca-600" />
        <path d="M10 9v14M22 9v14M10 16h12" stroke="#fff" strokeWidth="3" strokeLinecap="round" />
        <circle cx="22" cy="9" r="2.5" className="fill-marca-300" />
      </svg>
      HireMind
    </span>
  );
}

export function Cargando({ texto = "Cargando…" }: { texto?: string }) {
  return (
    <div className="flex items-center gap-2 py-10 text-sm text-zinc-500 justify-center">
      <LoaderCircle className="size-4 animate-spin" /> {texto}
    </div>
  );
}

export function Insignia({ children, tono = "neutro", className }: {
  children: ReactNode;
  tono?: "neutro" | "marca" | "verde" | "ambar" | "rojo";
  className?: string;
}) {
  const tonos = {
    neutro: "bg-zinc-100 text-zinc-700 ring-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:ring-zinc-700",
    marca: "bg-marca-50 text-marca-700 ring-marca-200 dark:bg-marca-950 dark:text-marca-300 dark:ring-marca-900",
    verde: "bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:ring-emerald-900",
    ambar: "bg-amber-50 text-amber-800 ring-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:ring-amber-900",
    rojo: "bg-rose-50 text-rose-700 ring-rose-200 dark:bg-rose-950/60 dark:text-rose-300 dark:ring-rose-900",
  };
  return (
    <span className={clsx("inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-xs font-medium ring-1 ring-inset", tonos[tono], className)}>
      {children}
    </span>
  );
}

const TONO_ESTADO = { cumple: "verde", parcial: "ambar", no_identificado: "neutro" } as const;
const ICONO_ESTADO = { cumple: CircleCheck, parcial: CircleMinus, no_identificado: CircleDashed };

export function InsigniaEstado({ estado }: { estado: Estado }) {
  const Icono = ICONO_ESTADO[estado];
  return (
    <Insignia tono={TONO_ESTADO[estado]}>
      <Icono className="size-3.5" /> {NOMBRE_ESTADO[estado]}
    </Insignia>
  );
}

/** Punto de color por criterio (vista compacta del ranking). */
export function PuntoEstado({ estado, titulo }: { estado: Estado; titulo: string }) {
  return (
    <span
      title={`${titulo}: ${NOMBRE_ESTADO[estado]}`}
      className={clsx(
        "inline-block size-2.5 rounded-full",
        estado === "cumple" && "bg-emerald-500",
        estado === "parcial" && "bg-amber-400",
        estado === "no_identificado" && "bg-zinc-300 dark:bg-zinc-700",
      )}
    />
  );
}

export function colorPuntaje(p: number) {
  if (p >= 75) return "bg-emerald-500";
  if (p >= 50) return "bg-marca-500";
  if (p >= 25) return "bg-amber-400";
  return "bg-zinc-400 dark:bg-zinc-600";
}

export function BarraPuntaje({ puntaje, className }: { puntaje: number; className?: string }) {
  return (
    <div className={clsx("h-1.5 w-full overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800", className)}>
      <div className={clsx("h-full rounded-full transition-all duration-500", colorPuntaje(puntaje))} style={{ width: `${puntaje}%` }} />
    </div>
  );
}

export function AnilloPuntaje({ puntaje, tam = 88 }: { puntaje: number; tam?: number }) {
  const r = 40, c = 2 * Math.PI * r;
  const color = puntaje >= 75 ? "stroke-emerald-500" : puntaje >= 50 ? "stroke-marca-500" : puntaje >= 25 ? "stroke-amber-400" : "stroke-zinc-400";
  return (
    <div className="relative shrink-0" style={{ width: tam, height: tam }}>
      <svg viewBox="0 0 100 100" className="size-full -rotate-90">
        <circle cx="50" cy="50" r={r} strokeWidth="9" fill="none" className="stroke-zinc-100 dark:stroke-zinc-800" />
        <circle cx="50" cy="50" r={r} strokeWidth="9" fill="none" strokeLinecap="round" className={clsx(color, "transition-all duration-700")}
          strokeDasharray={c} strokeDashoffset={c * (1 - puntaje / 100)} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xl font-semibold tabular-nums">{fmt(puntaje)}</span>
        <span className="text-[10px] uppercase tracking-wide text-zinc-500">de 100</span>
      </div>
    </div>
  );
}

export function Vacio({ icono, titulo, texto, accion }: { icono: ReactNode; titulo: string; texto: string; accion?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-300 px-6 py-14 text-center dark:border-zinc-700">
      <div className="mb-3 flex size-11 items-center justify-center rounded-full bg-marca-50 text-marca-600 dark:bg-marca-950 dark:text-marca-300">{icono}</div>
      <h3 className="font-medium">{titulo}</h3>
      <p className="mt-1 max-w-sm text-sm text-zinc-500">{texto}</p>
      {accion && <div className="mt-5">{accion}</div>}
    </div>
  );
}

export function Encabezado({ titulo, descripcion, acciones }: { titulo: string; descripcion?: ReactNode; acciones?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight">{titulo}</h1>
        {descripcion && <p className="mt-1 text-sm text-zinc-500">{descripcion}</p>}
      </div>
      {acciones && <div className="flex shrink-0 flex-wrap gap-2">{acciones}</div>}
    </div>
  );
}

export function Aviso({ tono = "rojo", children }: { tono?: "rojo" | "ambar" | "marca"; children: ReactNode }) {
  return (
    <div className={clsx(
      "rounded-lg border px-3.5 py-2.5 text-sm",
      tono === "rojo" && "border-rose-200 bg-rose-50 text-rose-800 dark:border-rose-900 dark:bg-rose-950/50 dark:text-rose-200",
      tono === "ambar" && "border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-900 dark:bg-amber-950/50 dark:text-amber-200",
      tono === "marca" && "border-marca-200 bg-marca-50 text-marca-900 dark:border-marca-900 dark:bg-marca-950/50 dark:text-marca-200",
    )}>
      {children}
    </div>
  );
}

export function useTema() {
  const [oscuro, setOscuro] = useState(() => document.documentElement.classList.contains("dark"));
  useEffect(() => {
    document.documentElement.classList.toggle("dark", oscuro);
    try { localStorage.setItem("tema", oscuro ? "oscuro" : "claro"); } catch { /* sin almacenamiento */ }
  }, [oscuro]);
  return [oscuro, () => setOscuro((o) => !o)] as const;
}

export function BotonTema() {
  const [oscuro, alternar] = useTema();
  return (
    <button onClick={alternar} className="btn-fantasma px-2" aria-label={oscuro ? "Usar tema claro" : "Usar tema oscuro"}>
      {oscuro ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </button>
  );
}

export const fmt = (n: number) => (Number.isInteger(n) ? String(n) : n.toFixed(1).replace(".", ","));

export function fechaCorta(iso: string | null | undefined) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("es-EC", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}
