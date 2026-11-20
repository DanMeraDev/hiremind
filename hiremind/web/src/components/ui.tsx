import clsx from "clsx";
import { CircleCheck, CircleDashed, CircleMinus, Moon, Sun } from "lucide-react";
import { useEffect, useState, type CSSProperties, type ReactNode } from "react";
import { Palabras, useCuenta } from "./anim";
import { NOMBRE_ESTADO, type Estado } from "../api";

/** Símbolo de la marca A: lupa que revisa + check que confirma, sobre el bloque menta. */
export function Simbolo({ className, animado = false }: { className?: string; animado?: boolean }) {
  return (
    <svg viewBox="0 0 64 64" className={clsx("shrink-0", className)} aria-hidden>
      <rect x="10" y="10" width="50" height="50" className={clsx("fill-menta", animado && "a-pop origin-center")} />
      <g className={clsx(animado && "a-entra")} style={animado ? { animationDelay: "220ms" } : undefined}>
        <circle cx="27" cy="27" r="16" fill="#fff" stroke="#0A0147" strokeWidth="7" />
        <path d="M39 39 L55 55" stroke="#0A0147" strokeWidth="9" strokeLinecap="square" />
      </g>
      <path d="M19 27.5 l6 6 l10.5 -12" fill="none" stroke="#FD696E" strokeWidth="5.5" strokeLinecap="square"
        className={clsx(animado && "a-traza")} style={animado ? ({ "--largo": 30, "--retraso": "560ms" } as CSSProperties) : undefined} />
    </svg>
  );
}

export function Logo({ className, animado = false, tam = "text-[26px]", invertido = false }: {
  className?: string; animado?: boolean; tam?: string; invertido?: boolean;
}) {
  return (
    <span className={clsx("flex items-center gap-2", className)}>
      <Simbolo className="size-8" animado={animado} />
      <span className={clsx("font-titulo pt-0.5 leading-none", tam)}>
        <span className={invertido ? "text-white" : "text-noche dark:text-white"}>HIRE</span>
        <span className={invertido ? "text-menta" : "text-coral dark:text-menta"}>MIND</span>
      </span>
    </span>
  );
}

export function Cargando({ texto = "Cargando…" }: { texto?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-sm font-semibold text-zinc-500" role="status">
      <span className="relative flex size-12 items-center justify-center border-2 border-(--tinta) bg-white shadow-xs dark:bg-zinc-900">
        <span className="absolute inset-x-2.5 top-3 h-1 bg-zinc-200 dark:bg-zinc-700" />
        <span className="absolute inset-x-2.5 top-5.5 h-1 bg-zinc-200 dark:bg-zinc-700" />
        <span className="absolute left-2.5 right-5 top-8 h-1 bg-zinc-200 dark:bg-zinc-700" />
        <Simbolo className="relative size-7 animate-[hm-lupa_1.6s_ease-in-out_infinite]" />
      </span>
      {texto}
    </div>
  );
}

type Tono = "neutro" | "marca" | "verde" | "ambar" | "rojo";
export function Insignia({ children, tono = "neutro", className }: { children: ReactNode; tono?: Tono; className?: string }) {
  const tonos: Record<Tono, string> = {
    neutro: "border-zinc-300 bg-white text-zinc-600 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300",
    marca: "border-noche bg-azul-claro text-noche dark:border-marca-400 dark:bg-marca-950 dark:text-marca-200",
    verde: "border-noche bg-menta text-noche dark:border-menta dark:bg-menta dark:text-noche",
    ambar: "border-noche bg-ambar text-noche dark:border-ambar dark:bg-ambar dark:text-noche",
    rojo: "border-noche bg-coral-claro text-rose-800 dark:border-coral dark:bg-rose-950 dark:text-rose-200",
  };
  return (
    <span className={clsx("inline-flex items-center gap-1 border-[1.5px] px-1.5 py-0.5 text-[11px] font-bold", tonos[tono], className)}>
      {children}
    </span>
  );
}

const TONO_ESTADO = { cumple: "verde", parcial: "ambar", no_identificado: "neutro" } as const;
const ICONO_ESTADO = { cumple: CircleCheck, parcial: CircleMinus, no_identificado: CircleDashed };

export function InsigniaEstado({ estado }: { estado: Estado }) {
  const Icono = ICONO_ESTADO[estado];
  return (
    <Insignia tono={TONO_ESTADO[estado]} className={clsx("uppercase tracking-wide", estado === "no_identificado" && "border-dashed")}>
      <Icono className="size-3.5" /> {NOMBRE_ESTADO[estado]}
    </Insignia>
  );
}

/** Cuadrito de color por criterio (vista compacta del ranking). */
export function PuntoEstado({ estado, titulo, i }: { estado: Estado; titulo: string; i?: number }) {
  return (
    <span
      title={`${titulo}: ${NOMBRE_ESTADO[estado]}`}
      style={i != null ? ({ "--i": i } as CSSProperties) : undefined}
      className={clsx(
        "inline-block size-2.5 border-[1.5px] border-noche dark:border-zinc-950",
        i != null && "a-pop",
        estado === "cumple" && "bg-menta",
        estado === "parcial" && "bg-ambar",
        estado === "no_identificado" && "border-dashed border-zinc-400 bg-white dark:border-zinc-500 dark:bg-zinc-900",
      )}
    />
  );
}

export function colorPuntaje(p: number) {
  if (p >= 75) return "bg-menta";
  if (p >= 50) return "bg-azul";
  if (p >= 25) return "bg-ambar";
  return "bg-zinc-300 dark:bg-zinc-600";
}

export function BarraPuntaje({ puntaje, className, i }: { puntaje: number; className?: string; i?: number }) {
  return (
    <div className={clsx("h-2.5 w-full border-[1.5px] border-(--tinta) bg-azul-claro dark:bg-zinc-800", className)}>
      <div className={clsx("a-crece-x h-full border-r-[1.5px] border-(--tinta) transition-[width] duration-700 ease-rebote", colorPuntaje(puntaje), puntaje === 0 && "border-r-0")}
        style={{ width: `${puntaje}%`, "--i": i ?? 0 } as CSSProperties} />
    </div>
  );
}

const TRAZO_PUNTAJE = (p: number) => (p >= 75 ? "stroke-menta" : p >= 50 ? "stroke-azul" : p >= 25 ? "stroke-ambar" : "stroke-zinc-400");

/** Anillo que se llena con rebote mientras la cifra cuenta (manual A, “Puntaje · llenado con rebote”). */
export function AnilloPuntaje({ puntaje, tam = 92 }: { puntaje: number; tam?: number }) {
  const v = useCuenta(puntaje, 900);
  const r = 38, c = 2 * Math.PI * r;
  return (
    <div className="relative shrink-0" style={{ width: tam, height: tam }}>
      <svg viewBox="0 0 100 100" className="size-full -rotate-90">
        <circle cx="50" cy="50" r={r} strokeWidth="13" fill="none" className="stroke-azul-claro dark:stroke-zinc-800" />
        <circle cx="50" cy="50" r={r} strokeWidth="13" fill="none" className={TRAZO_PUNTAJE(puntaje)}
          strokeDasharray={c} strokeDashoffset={c * (1 - Math.max(0, v) / 100)} />
        <circle cx="50" cy="50" r={r + 6.5} strokeWidth="2" fill="none" className="stroke-(--tinta)" />
        <circle cx="50" cy="50" r={r - 6.5} strokeWidth="2" fill="none" className="stroke-(--tinta)" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-titulo text-3xl tabular-nums">{fmt(Math.round(v * 10) / 10)}</span>
        <span className="-mt-0.5 text-[9px] font-bold uppercase tracking-wider text-zinc-500">de 100</span>
      </div>
    </div>
  );
}

export function Vacio({ icono, titulo, texto, accion }: { icono: ReactNode; titulo: string; texto: string; accion?: ReactNode }) {
  return (
    <div className="a-sube relative flex flex-col items-center justify-center overflow-hidden border-2 border-dashed border-(--tinta) bg-white px-6 py-14 text-center dark:bg-zinc-900">
      <span className="absolute -left-6 -bottom-6 size-16 rounded-full border-[10px] border-coral" aria-hidden />
      <div className="a-pop mb-4 flex size-12 items-center justify-center border-2 border-(--tinta) bg-menta text-noche shadow-xs">{icono}</div>
      <h3 className="font-titulo text-3xl">{titulo}</h3>
      <p className="mt-1 max-w-sm text-sm text-zinc-500">{texto}</p>
      {accion && <div className="mt-5">{accion}</div>}
    </div>
  );
}

export function Encabezado({ titulo, descripcion, acciones }: { titulo: string; descripcion?: ReactNode; acciones?: ReactNode }) {
  return (
    <div className="mb-7 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        <Palabras como="h1" texto={titulo.toUpperCase()} className="font-titulo text-5xl" />
        {descripcion && <p className="a-sube mt-1 text-sm font-medium text-zinc-500" style={{ "--i": 3 } as CSSProperties}>{descripcion}</p>}
      </div>
      {acciones && <div className="a-sube flex shrink-0 flex-wrap gap-2.5" style={{ "--i": 4 } as CSSProperties}>{acciones}</div>}
    </div>
  );
}

export function Aviso({ tono = "rojo", children }: { tono?: "rojo" | "ambar" | "marca"; children: ReactNode }) {
  return (
    <div className={clsx(
      "a-sube border-2 border-l-8 border-(--tinta) px-3.5 py-2.5 text-sm font-medium",
      tono === "rojo" && "border-l-coral bg-coral-claro text-rose-800 dark:bg-rose-950 dark:text-rose-200",
      tono === "ambar" && "border-l-ambar bg-amber-50 text-amber-900 dark:bg-amber-950 dark:text-amber-200",
      tono === "marca" && "border-l-azul bg-azul-claro text-noche dark:bg-marca-950 dark:text-marca-200",
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
