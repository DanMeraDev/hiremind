// Movimiento de la marca A. Patrones tomados de las demos de Optimion:
// cifras que cuentan, entradas al hacer scroll, titulares palabra por palabra y chips con rebote.
import clsx from "clsx";
import { useEffect, useRef, useState, type CSSProperties, type ElementType, type ReactNode } from "react";

export const sinMovimiento = () =>
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Número que sube desde el valor anterior hasta `valor` (curva exponencial de salida). */
export function useCuenta(valor: number, ms = 900, activo = true) {
  const [v, setV] = useState(sinMovimiento() || !activo ? valor : 0);
  const desde = useRef(sinMovimiento() || !activo ? valor : 0);
  useEffect(() => {
    if (!activo) return;
    if (sinMovimiento()) { setV(valor); desde.current = valor; return; }
    const a = desde.current, t0 = performance.now();
    let id = 0;
    const paso = (t: number) => {
      const k = Math.min(1, (t - t0) / ms);
      const x = a + (valor - a) * (1 - Math.pow(2, -10 * k));
      setV(k < 1 ? x : valor);
      if (k < 1) id = requestAnimationFrame(paso);
      else desde.current = valor;
    };
    id = requestAnimationFrame(paso);
    return () => { cancelAnimationFrame(id); desde.current = valor; };
  }, [valor, ms, activo]);
  return v;
}

const coma = (n: number, dec: number) => n.toFixed(dec).replace(".", ",");

/** Cifra animada. `decimales` fija el formato final (0 → entero). */
export function Cifra({ valor, decimales, sufijo = "", ms, activo = true }: {
  valor: number; decimales?: number; sufijo?: string; ms?: number; activo?: boolean;
}) {
  const v = useCuenta(valor, ms, activo);
  const dec = decimales ?? (Number.isInteger(valor) ? 0 : 1);
  return <span className="tabular-nums">{coma(v, dec)}{sufijo}</span>;
}

/** true la primera vez que el elemento entra en pantalla. */
export function useVisible<T extends Element>(margen = "0px 0px -12% 0px") {
  const ref = useRef<T>(null);
  const [visto, setVisto] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el || visto) return;
    if (sinMovimiento() || !("IntersectionObserver" in window)) { setVisto(true); return; }
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVisto(true); io.disconnect(); } }, { rootMargin: margen });
    io.observe(el);
    return () => io.disconnect();
  }, [margen, visto]);
  return [ref, visto] as const;
}

/** Bloque que sube y aparece al hacer scroll. */
export function Revela({ children, retraso = 0, como: Como = "div", className, style }: {
  children: ReactNode; retraso?: number; como?: ElementType; className?: string; style?: CSSProperties;
}) {
  const [ref, visto] = useVisible<HTMLElement>();
  return (
    <Como ref={ref} className={clsx("transition-[opacity,transform] duration-[900ms] ease-salida", !visto && "translate-y-5 opacity-0", className)}
      style={{ transitionDelay: `${retraso}ms`, ...style }}>
      {children}
    </Como>
  );
}

/** Titular: cada palabra sube desde su máscara, una tras otra. Las palabras entre *asteriscos* van en coral. */
export function Palabras({ texto, como: Como = "h2", className, retraso = 0, claseAcento = "text-coral" }: {
  texto: string; como?: ElementType; className?: string; retraso?: number; claseAcento?: string;
}) {
  const [ref, visto] = useVisible<HTMLElement>();
  let acento = false;
  const palabras = texto.split(/\s+/).map((w) => {
    const abre = w.startsWith("*"), cierra = w.endsWith("*");
    if (abre) acento = true;
    const r = { w: w.replace(/\*/g, ""), acento };
    if (cierra) acento = false;
    return r;
  });
  return (
    <Como ref={ref} className={className} aria-label={texto.replace(/\*/g, "")}>
      {palabras.map(({ w, acento }, i) => (
        <span key={i} aria-hidden className="inline-block overflow-hidden pb-[0.08em] align-top">
          <span className={clsx("inline-block transition-transform duration-[900ms] ease-salida", !visto && "translate-y-[105%]", acento && claseAcento)}
            style={{ transitionDelay: `${retraso + i * 50}ms` }}>
            {w}
          </span>
          {i < palabras.length - 1 && " "}
        </span>
      ))}
    </Como>
  );
}

/** Hijos que aparecen con rebote, uno tras otro, cuando el grupo entra en pantalla. */
export function Pops({ children, className, paso = 70 }: { children: ReactNode[]; className?: string; paso?: number }) {
  const [ref, visto] = useVisible<HTMLDivElement>("0px 0px -20% 0px");
  return (
    <div ref={ref} className={className}>
      {children.map((c, i) => (
        <div key={i} className={clsx("transition-[opacity,transform,filter] duration-500 ease-rebote", !visto && "scale-80 opacity-0 grayscale")}
          style={{ transitionDelay: `${i * paso}ms` }}>
          {c}
        </div>
      ))}
    </div>
  );
}
