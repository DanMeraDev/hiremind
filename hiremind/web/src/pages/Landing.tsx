// Página de venta (marca A · "Energía"). Hoy vive dentro de la app; está pensada para separarse a su propio sitio.
// Movimiento inspirado en la landing de Optimion: scroll suave (Lenis), titulares por palabra, escenas que se
// reproducen solas mientras están a la vista, cinta, pasos ligados al scroll y logotipo gigante en el pie.
import clsx from "clsx";
import Lenis from "lenis";
import {
  ArrowRight, BadgeCheck, Check, CreditCard, Download, EyeOff, FileText, ListChecks, Lock, Quote, ScanLine, ShieldCheck, Star, Trophy, UserCheck,
} from "lucide-react";
import { useEffect, useRef, useState, type CSSProperties, type ReactNode, type RefObject } from "react";
import { Link } from "react-router";
import { Cifra, Palabras, Pops, Revela, sinMovimiento, useVisible } from "../components/anim";
import { BotonTema, Logo, PuntoEstado, Simbolo } from "../components/ui";
import type { Estado } from "../api";

/* ───────────────────────── utilidades ───────────────────────── */

let lenis: Lenis | null = null;
function irA(id: string) {
  const el = document.getElementById(id);
  if (!el) return;
  if (lenis) lenis.scrollTo(el, { offset: -90, duration: 1.3 });
  else el.scrollIntoView({ behavior: sinMovimiento() ? "auto" : "smooth" });
}

/** Texto del botón que cambia de lugar al pasar el mouse (como en Optimion). */
function Etiqueta({ children }: { children: ReactNode }) {
  return (
    <span className="relative inline-flex overflow-hidden whitespace-nowrap">
      <span className="transition-transform duration-300 ease-salida group-hover:-translate-y-full">{children}</span>
      <span aria-hidden className="absolute inset-0 translate-y-full transition-transform duration-300 ease-salida group-hover:translate-y-0">{children}</span>
    </span>
  );
}

/** Espera que solo avanza mientras la escena está a la vista y la pestaña activa. */
function esperar(ms: number, visible: RefObject<boolean>, vivo: { v: boolean }) {
  return new Promise<void>((ok) => {
    let t = 0;
    const paso = () => {
      if (!vivo.v) return;
      if (visible.current && !document.hidden) t += 100;
      if (t >= ms) ok(); else setTimeout(paso, 100);
    };
    paso();
  });
}

/* ───────────────────────── escena de la portada: el ranking se arma solo ───────────────────────── */

type Cand = { n: string; p: number; e: Estado[] };
const LLEGADA: Cand[] = [
  { n: "Luis Andrango", p: 57.5, e: ["parcial", "parcial", "cumple", "no_identificado", "cumple"] },
  { n: "Andrea Salazar", p: 100, e: ["cumple", "cumple", "cumple", "cumple", "cumple"] },
  { n: "Pedro Guamán", p: 32.5, e: ["parcial", "no_identificado", "parcial", "no_identificado", "cumple"] },
  { n: "Carlos Ortiz", p: 90, e: ["cumple", "cumple", "cumple", "cumple", "no_identificado"] },
  { n: "María José Paredes", p: 87.5, e: ["parcial", "cumple", "cumple", "cumple", "cumple"] },
];
const RANGO = [...LLEGADA].sort((a, b) => b.p - a.p).map((c) => c.n);
const ALTO = 58;

function EscenaRanking() {
  const caja = useRef<HTMLDivElement>(null);
  const visible = useRef(true);
  const [n, setN] = useState(0);
  const [listos, setListos] = useState(0);
  const [ordenado, setOrdenado] = useState(false);

  useEffect(() => {
    const el = caja.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => { visible.current = e.isIntersecting; });
    io.observe(el);
    if (sinMovimiento()) { setN(5); setListos(5); setOrdenado(true); return () => io.disconnect(); }
    const vivo = { v: true };
    (async () => {
      while (vivo.v) {
        setN(0); setListos(0); setOrdenado(false);
        await esperar(500, visible, vivo);
        for (let i = 0; i < LLEGADA.length && vivo.v; i++) {
          setN(i + 1); await esperar(700, visible, vivo);
          setListos(i + 1); await esperar(450, visible, vivo);
        }
        await esperar(600, visible, vivo); setOrdenado(true);
        await esperar(4200, visible, vivo);
      }
    })();
    return () => { vivo.v = false; io.disconnect(); };
  }, []);

  return (
    <div ref={caja} className="relative">
      <div className="border-[3px] border-noche bg-white shadow-[10px_10px_0_0_#0A0147] dark:bg-zinc-900">
        <div className="flex items-center justify-between gap-3 border-b-[3px] border-noche bg-noche px-4 py-2.5">
          <Logo tam="text-xl" invertido />
          <span className="truncate text-[11px] font-bold text-white/75">Asistente contable · Ranking</span>
        </div>
        <div className="flex items-center justify-between border-b-2 border-noche px-4 py-2 text-[11px] font-extrabold uppercase italic tracking-wider text-noche dark:text-zinc-200">
          <span>{ordenado ? "Ordenado de mayor a menor" : n === 0 ? "Esperando hojas de vida" : `Revisando CV ${n} de 5`}</span>
          <span className="tabular-nums">{listos}/5</span>
        </div>
        <div className="relative" style={{ height: ALTO * LLEGADA.length }}>
          {LLEGADA.map((c, i) => {
            const pos = ordenado ? RANGO.indexOf(c.n) : i;
            const llego = i < n, listo = i < listos, top = ordenado && pos < 3;
            return (
              <div key={c.n}
                className={clsx(
                  "absolute inset-x-0 flex items-center gap-3 border-b-2 border-zinc-100 px-4 transition-[top,opacity,transform,background-color] duration-700 ease-rebote dark:border-zinc-800",
                  llego ? "translate-x-0 opacity-100" : "-translate-x-8 opacity-0",
                  top && "bg-menta-claro dark:bg-marca-950",
                )}
                style={{ top: pos * ALTO, height: ALTO }}>
                <span className={clsx("flex size-8 shrink-0 items-center justify-center border-2 font-titulo text-lg transition-colors duration-300",
                  top ? "border-noche bg-coral text-noche" : "border-zinc-300 text-zinc-500 dark:border-zinc-600")}>
                  {ordenado ? pos + 1 : <FileText className="size-4" />}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="flex items-center gap-1 truncate text-sm font-bold text-noche dark:text-white">
                    {c.n} {top && <Star className="a-pop size-3.5 shrink-0 fill-ambar text-noche dark:text-ambar" />}
                  </p>
                  <div className="mt-1 flex h-2.5 gap-1">
                    {listo ? c.e.map((e, j) => <PuntoEstado key={j} estado={e} titulo="" i={j} />)
                      : llego && <span className="escaneo h-2.5 w-24 bg-zinc-100 dark:bg-zinc-800" />}
                  </div>
                </div>
                <div className="w-20 shrink-0 text-right">
                  <span className="font-titulo text-2xl leading-none text-noche dark:text-white">{listo ? <Cifra valor={c.p} ms={700} /> : "—"}</span>
                  <div className="mt-1 h-2.5 border-[1.5px] border-noche bg-azul-claro dark:bg-zinc-800">
                    <div className={clsx("h-full transition-[width] duration-700 ease-rebote", c.p >= 75 ? "bg-menta" : c.p >= 50 ? "bg-azul" : "bg-ambar")}
                      style={{ width: listo ? `${c.p}%` : 0 }} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="border-t-2 border-noche p-3.5">
          <p className="text-[10px] font-extrabold uppercase italic tracking-wider text-zinc-500">Evidencia · Facturación electrónica SRI</p>
          <blockquote className="mt-1.5 flex items-center gap-2 border-l-4 border-menta bg-zinc-50 px-3 py-1.5 text-xs font-medium text-noche dark:bg-zinc-800 dark:text-zinc-100">
            <Quote className="size-3 shrink-0 text-coral" />
            <span className="flex-1">«Manejo de facturación electrónica SRI»</span>
            <BadgeCheck className={clsx("size-4 shrink-0 text-emerald-600 transition-transform duration-500 ease-rebote dark:text-menta", listos > 1 ? "scale-100" : "scale-0")} />
          </blockquote>
        </div>
      </div>
      <div className={clsx("absolute -bottom-5 -left-3 flex items-center gap-2 border-2 border-noche bg-ambar px-3 py-1.5 text-xs font-extrabold uppercase text-noche shadow-[4px_4px_0_0_#0A0147] transition-[transform,opacity] duration-500 ease-rebote sm:-left-8",
        ordenado ? "translate-y-0 -rotate-3 opacity-100" : "translate-y-3 opacity-0")}>
        <UserCheck className="size-4" /> Ahora usted revisa y decide
      </div>
    </div>
  );
}

/* ───────────────────────── cinta ───────────────────────── */

const FRASES = ["100 % local", "Cada dato con su cita", "Sin edad ni estado civil", "Una persona decide", "Corrija con un clic", "Exporte en CSV"];
function Cinta() {
  return (
    <div className="overflow-hidden border-y-[3px] border-noche bg-noche py-4 text-white" aria-hidden>
      <div className="flex w-max animate-[hm-cinta_32s_linear_infinite] motion-reduce:animate-none">
        {[0, 1].map((k) => (
          <div key={k} className="flex shrink-0 gap-10 pr-10">
            {[...FRASES, ...FRASES].map((f, i) => (
              <span key={i} className="flex items-center gap-10 font-titulo text-3xl tracking-wide">
                {f} <span className={clsx("size-4", ["bg-menta", "bg-coral", "bg-azul"][i % 3])} />
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ───────────────────────── cómo funciona: pasos ligados al scroll ───────────────────────── */

const PASOS = [
  { icono: ListChecks, t: "Defina la vacante", d: "Criterios de formación, experiencia, habilidades e idiomas, cada uno con su peso. HireMind no acepta criterios sobre edad, género o estado civil.", color: "bg-menta" },
  { icono: FileText, t: "Suba los PDF", d: "Arrastre todas las hojas de vida. Los escaneados o ilegibles se separan para revisión manual, sin puntaje inventado.", color: "bg-coral" },
  { icono: ShieldCheck, t: "El agente verifica", d: "Quita los datos personales, extrae cada dato con una cita del CV y comprueba que la cita exista. Si no existe, el dato no suma.", color: "bg-azul" },
  { icono: Trophy, t: "Usted decide", d: "Recibe un ranking justificado con evidencias. Revisa el top 5, corrige lo que haga falta y exporta en CSV.", color: "bg-ambar" },
];

const FONDO_PASO = ["bg-menta-claro", "bg-coral-claro", "bg-azul-claro", "bg-amber-50"];

function VisualPaso({ i }: { i: number }) {
  if (i === 0)
    return (
      <div className="space-y-3">
        {([["Formación", "Contabilidad · CPA", 25], ["Experiencia", "2 años en contabilidad", 30], ["Habilidad", "Excel avanzado", 20], ["Habilidad", "Facturación SRI", 15], ["Idioma", "Inglés básico", 10]] as const).map(([t, nom, p], j) => (
          <div key={j} className="a-entra flex items-center gap-3 border-2 border-noche bg-white px-3 py-2 dark:bg-zinc-900" style={{ "--i": j } as CSSProperties}>
            <span className="w-20 text-[10px] font-extrabold uppercase italic text-zinc-500 sm:w-24">{t}</span>
            <span className="flex-1 text-sm font-bold text-noche dark:text-white">{nom}</span>
            <span className="border-2 border-noche bg-menta px-1.5 font-titulo text-lg text-noche">{p} %</span>
          </div>
        ))}
      </div>
    );
  if (i === 1)
    return (
      <div className="relative h-60">
        {[0, 1, 2, 3, 4].map((j) => (
          <div key={j} className="a-pop absolute flex h-36 w-24 flex-col gap-2 border-2 border-noche bg-white p-3 shadow-[4px_4px_0_0_#0A0147] sm:w-28 dark:bg-zinc-900"
            style={{ left: `${4 + j * 16}%`, top: `${j % 2 ? 22 : 4}%`, rotate: `${(j - 2) * 5}deg`, "--i": j } as CSSProperties}>
            <span className="font-titulo text-base text-coral">PDF</span>
            {[80, 60, 90, 50, 70].map((w, k) => <span key={k} className="h-1.5 bg-zinc-200 dark:bg-zinc-700" style={{ width: `${w}%` }} />)}
          </div>
        ))}
      </div>
    );
  if (i === 2)
    return (
      <div className="space-y-3 border-2 border-noche bg-white p-4 dark:bg-zinc-900">
        <p className="text-sm font-medium leading-relaxed text-noche dark:text-zinc-100">
          <span className="text-zinc-400 line-through decoration-coral decoration-2">Edad: 27 años · Estado civil: soltera</span><br />
          Asistente contable en Distribuidora Andina (2022 – actual).<br />
          Manejo de <mark className="bg-transparent bg-[linear-gradient(transparent_55%,#2EE5A7_55%)] text-inherit">Excel avanzado (tablas dinámicas)</mark> y
          {" "}<mark className="bg-transparent bg-[linear-gradient(transparent_55%,#2EE5A7_55%)] text-inherit">facturación electrónica SRI</mark>.
        </p>
        <div className="flex flex-wrap gap-2">
          <span className="a-pop flex items-center gap-1 border-2 border-noche bg-menta px-2 py-0.5 text-[11px] font-extrabold uppercase text-noche" style={{ "--i": 2 } as CSSProperties}><BadgeCheck className="size-3.5" /> Cita verificada</span>
          <span className="a-pop flex items-center gap-1 border-2 border-noche bg-coral-claro px-2 py-0.5 text-[11px] font-extrabold uppercase text-noche" style={{ "--i": 4 } as CSSProperties}><EyeOff className="size-3.5" /> 2 datos excluidos</span>
        </div>
      </div>
    );
  return (
    <div className="space-y-2">
      {([["Andrea Salazar", 100], ["Carlos Ortiz", 90], ["María José Paredes", 87.5]] as const).map(([nom, p], j) => (
        <div key={j} className="a-entra flex items-center gap-3 border-2 border-noche bg-white px-3 py-2 dark:bg-zinc-900" style={{ "--i": j } as CSSProperties}>
          <span className="flex size-7 items-center justify-center border-2 border-noche bg-coral font-titulo text-noche">{j + 1}</span>
          <span className="flex-1 text-sm font-bold text-noche dark:text-white">{nom}</span>
          <span className="font-titulo text-2xl text-noche dark:text-white"><Cifra valor={p} /></span>
        </div>
      ))}
      <div className="a-pop mt-4 flex items-center gap-2 border-2 border-noche bg-ambar px-3 py-2 text-sm font-extrabold text-noche" style={{ "--i": 4 } as CSSProperties}>
        <UserCheck className="size-5" /> La decisión final es suya
      </div>
    </div>
  );
}

function ComoFunciona() {
  const [activo, setActivo] = useState(0);
  const refs = useRef<(HTMLLIElement | null)[]>([]);
  useEffect(() => {
    // el paso activo es el último cuyo inicio ya pasó la mitad de la pantalla
    const medir = () => {
      let k = 0;
      refs.current.forEach((el, i) => { if (el && el.getBoundingClientRect().top < window.innerHeight * 0.55) k = i; });
      setActivo(k);
    };
    medir();
    window.addEventListener("scroll", medir, { passive: true });
    return () => window.removeEventListener("scroll", medir);
  }, []);
  return (
    <section id="como" className="relative bg-white dark:bg-zinc-950">
      <span aria-hidden className="absolute right-[12%] top-0 h-4 w-48 bg-azul" />
      <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
        <p className="text-sm font-extrabold uppercase italic tracking-wider text-rose-600 dark:text-coral">Cómo funciona</p>
        <Palabras texto="DE UNA CARPETA DE PDF A UN *RANKING* QUE PUEDE EXPLICAR" className="mt-2 max-w-3xl font-titulo text-5xl text-noche sm:text-7xl dark:text-white" />
        <div className="mt-14 grid gap-12 lg:grid-cols-2">
          <ol className="space-y-12 lg:space-y-[28vh] lg:pb-[18vh]">
            {PASOS.map((p, i) => (
              <li key={p.t} data-paso={i} ref={(el) => { refs.current[i] = el; }}
                className={clsx("border-l-[6px] pl-5 transition-[opacity,border-color] duration-500",
                  activo === i ? "border-coral opacity-100" : "border-zinc-200 lg:opacity-40 dark:border-zinc-800")}>
                <div className="flex items-center gap-3">
                  <span className={clsx("flex size-12 items-center justify-center border-2 border-noche text-noche transition-transform duration-500 ease-rebote", p.color, activo === i && "-rotate-6 scale-110")}>
                    <p.icono className="size-6" />
                  </span>
                  <span className="font-titulo text-2xl text-zinc-500">Paso {i + 1}</span>
                </div>
                <h3 className="mt-3 font-titulo text-4xl text-noche dark:text-white">{p.t}</h3>
                <p className="mt-2 max-w-md font-medium leading-relaxed text-zinc-600 dark:text-zinc-300">{p.d}</p>
                <div className="mt-6 lg:hidden"><VisualPaso i={i} /></div>
              </li>
            ))}
          </ol>
          <div className="hidden lg:block">
            <div className="sticky top-28">
              <div className={clsx("relative border-[3px] border-noche p-6 shadow-[10px_10px_0_0_#0A0147] transition-colors duration-500 dark:bg-zinc-900", FONDO_PASO[activo])}>
                <span className="absolute -top-4 left-6 border-2 border-noche bg-white px-2 font-titulo text-xl text-noche">Paso {activo + 1} de 4</span>
                <div key={activo} className="min-h-72 pt-3"><VisualPaso i={activo} /></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ───────────────────────── resto de secciones ───────────────────────── */

const BENEFICIOS = [
  { i: Lock, t: "100 % local", d: "El modelo corre en su computador. Las hojas de vida nunca salen de su oficina.", c: "bg-menta" },
  { i: Quote, t: "Cada dato con su cita", d: "El agente copia la frase del CV que respalda cada dato. Si la frase no existe, el dato no suma puntos.", c: "bg-coral" },
  { i: EyeOff, t: "Equidad desde el inicio", d: "Edad, estado civil, nacionalidad y otros datos personales se quitan antes de que el modelo lea el CV.", c: "bg-azul" },
  { i: UserCheck, t: "Una persona decide", d: "No se descarta a nadie de forma automática. El ranking es una ayuda; la decisión es suya.", c: "bg-ambar" },
  { i: ScanLine, t: "Sin sorpresas", d: "Los PDF escaneados o ilegibles se separan para revisión manual en lugar de recibir un puntaje inventado.", c: "bg-menta" },
  { i: Download, t: "Corrija y exporte", d: "Ajuste cualquier criterio con un clic y descargue el ranking en CSV para su equipo.", c: "bg-coral" },
];

const PREGUNTAS = [
  ["¿Necesito internet o una cuenta en la nube?", "No. El modelo de lenguaje corre en el mismo computador con LM Studio y las hojas de vida nunca salen de su oficina. Solo el Plan Escala ofrece, si usted lo activa, procesar en la nube campañas masivas."],
  ["¿Tengo que pagar cada mes?", "No. La licencia base se paga una sola vez y es suya para siempre. Si su empresa crece y necesita más vacantes o más CV, puede activar una expansión anual; mientras no la necesite, su costo mensual es $0."],
  ["¿Por qué la expansión es anual y no mensual?", "Porque las PYMEs contratan por temporadas. Un pago anual cubre los picos de contratación, se presupuesta una sola vez y cuesta menos que doce cuotas; no paga nada en los meses sin vacantes."],
  ["¿La IA decide a quién contratar?", "No. Ordena y justifica con evidencias. Ningún CV se descarta automáticamente y la decisión final es siempre de una persona."],
  ["¿Qué pasa si la IA se equivoca?", "Cada dato tiene una cita del CV que usted puede leer. Si un criterio está mal evaluado, lo corrige con un clic y el puntaje se recalcula."],
  ["¿Qué computador necesito?", "Una PC de oficina con 16 GB de RAM. Con tarjeta gráfica cada CV tarda alrededor de 10 segundos; sin ella, más."],
  ["¿Cómo se evita la discriminación?", "La edad, el estado civil, la nacionalidad y otros datos personales se eliminan antes del análisis, y no se permiten criterios sobre ellos."],
];

/* ───────────────────────── planes: base perpetua + expansiones anuales ───────────────────────── */

const PLANES = [
  {
    nombre: "Licencia base", precio: 299, periodo: "pago único", nota: "Para empezar", color: "bg-menta", destacado: true,
    items: ["Suya para siempre, en 1 equipo", "Hasta 3 vacantes activas a la vez", "60 CV por vacante · 300 CV al año", "Modelo local Qwen 4B, sin internet", "$0 en tokens: sin costo por uso"],
  },
  {
    nombre: "Plan Crecimiento", precio: 149, periodo: "por año", nota: "Cuando su equipo crece", color: "bg-azul", destacado: false,
    items: ["Hasta 12 vacantes activas a la vez", "Hasta 1 500 CV al año", "Hasta 3 equipos con respaldos cruzados", "Actualización anual del modelo (p. ej. Qwen 7B)", "Soporte técnico preventivo"],
  },
  {
    nombre: "Plan Escala", precio: 299, periodo: "por año", nota: "Alto volumen", color: "bg-coral", destacado: false,
    items: ["Vacantes y CV sin límite local", "Hasta 5 equipos y respaldo automático", "Nube opcional para campañas masivas", "La misma interfaz, sin reinstalar", "Soporte prioritario"],
  },
];

const SERVICIOS = [
  ["Setup remoto", "$75", "Obligatorio · auditoría del equipo, instalación remota y 45 min de capacitación"],
  ["Setup presencial", "$120", "Opcional · instalación en su oficina y pruebas con sus CV reales"],
  ["Soporte puntual", "$85", "Bajo demanda · para la licencia base sin expansión activa"],
];

function Planes() {
  return (
    <section id="planes" className="relative overflow-hidden bg-zinc-50 dark:bg-zinc-900">
      <span aria-hidden className="absolute left-[8%] top-0 h-4 w-44 bg-menta" />
      <span aria-hidden className="absolute -right-20 bottom-24 hidden size-52 rounded-full border-[32px] border-azul lg:block" />
      <div className="relative mx-auto max-w-6xl px-4 py-24 sm:px-6">
        <p className="text-sm font-extrabold uppercase italic tracking-wider text-rose-600 dark:text-coral">Planes</p>
        <Palabras texto="COMPRE HOY, *ESCALE* CUANDO CREZCA" className="mt-2 max-w-3xl font-titulo text-5xl text-noche sm:text-7xl dark:text-white" />
        <Revela retraso={200}>
          <p className="mt-4 max-w-2xl text-lg font-medium leading-relaxed text-zinc-600 dark:text-zinc-300">
            Un solo pago por la licencia base, sin mensualidades. Si su empresa crece, amplíe la capacidad con una expansión anual;
            si no, su costo sigue en <b className="text-noche dark:text-white">$0 al mes</b>.
          </p>
        </Revela>

        <Pops className="mt-12 grid gap-6 lg:grid-cols-3" paso={110}>
          {PLANES.map((pl) => (
            <div key={pl.nombre} className={clsx("relative flex h-full flex-col border-[3px] border-noche bg-white p-6 transition-transform duration-300 ease-rebote hover:-translate-y-1 dark:bg-zinc-950",
              pl.destacado ? "shadow-[10px_10px_0_0_#0A0147] dark:shadow-[10px_10px_0_0_#2EE5A7]" : "shadow-[6px_6px_0_0_#0A0147] dark:shadow-[6px_6px_0_0_#000]")}>
              <span className={clsx("absolute -top-4 left-5 border-2 border-noche px-2 py-0.5 text-[11px] font-extrabold uppercase italic text-noche", pl.color)}>{pl.nota}</span>
              <h3 className="mt-2 font-titulo text-3xl text-noche dark:text-white">{pl.nombre}</h3>
              <p className="mt-3 flex items-end gap-2 text-noche dark:text-white">
                <span className="font-titulo text-7xl leading-[0.8]">$<Cifra valor={pl.precio} ms={1200} /></span>
                <span className="pb-1 text-sm font-extrabold uppercase">{pl.periodo}</span>
              </p>
              <ul className="mt-6 flex-1 space-y-2.5">
                {pl.items.map((it) => (
                  <li key={it} className="flex gap-2.5 text-sm font-semibold text-zinc-700 dark:text-zinc-200">
                    <span className={clsx("mt-0.5 flex size-5 shrink-0 items-center justify-center border-2 border-noche text-noche", pl.color)}><Check className="size-3" strokeWidth={3.5} /></span>
                    {it}
                  </li>
                ))}
              </ul>
              {pl.destacado
                ? <p className="mt-6 border-t-2 border-noche pt-4 text-xs font-bold text-zinc-600 dark:border-zinc-700 dark:text-zinc-300">Más el setup obligatorio. Sin cuotas después.</p>
                : <p className="mt-6 border-t-2 border-noche pt-4 text-xs font-bold text-zinc-600 dark:border-zinc-700 dark:text-zinc-300">Se suma a la licencia base. Renovación anual opcional.</p>}
            </div>
          ))}
        </Pops>

        {/* ticket de entrada */}
        <Revela className="mt-14 grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <div className="border-[3px] border-noche bg-noche p-6 text-white shadow-[8px_8px_0_0_#2EE5A7]">
            <p className="text-xs font-extrabold uppercase italic tracking-wider text-menta">Ticket de entrada · pago único</p>
            <div className="mt-3 flex flex-wrap items-center gap-3 font-titulo text-5xl sm:text-6xl">
              <span>$299</span><span className="text-coral">+</span><span>$75</span><span className="text-coral">=</span>
              <span className="bg-menta px-2 text-noche">$<Cifra valor={374} ms={1400} /></span>
            </div>
            <p className="mt-3 text-sm font-medium text-white/80">Licencia base + setup remoto. Pague con tarjeta diferida a 3 o 6 meses sin intereses, o 50 % al contratar y 50 % al terminar la instalación.</p>
            <p className="mt-4 flex items-start gap-2 border-t-2 border-white/15 pt-4 text-sm font-semibold text-white/90">
              <CreditCard className="mt-0.5 size-4 shrink-0 text-menta" />
              Una agencia cobra entre $230 y $500 por una sola contratación. Con HireMind, aun sumando el Plan Crecimiento, el año completo cuesta menos.
            </p>
          </div>
          <ul className="space-y-3">
            {SERVICIOS.map(([n, pr, d], i) => (
              <li key={n} className="a-entra flex items-center gap-4 border-2 border-noche bg-white px-4 py-3 dark:bg-zinc-950" style={{ "--i": i } as CSSProperties}>
                <span className="w-16 shrink-0 font-titulo text-3xl text-noche dark:text-white">{pr}</span>
                <span>
                  <span className="block text-sm font-extrabold uppercase text-noche dark:text-white">{n}</span>
                  <span className="block text-xs font-medium text-zinc-600 dark:text-zinc-300">{d}</span>
                </span>
              </li>
            ))}
          </ul>
        </Revela>
        <p className="mt-6 text-xs font-semibold text-zinc-500">Precios en dólares (USD). Propuesta comercial del proyecto académico.</p>
      </div>
    </section>
  );
}

function Pregunta({ p, r, i }: { p: string; r: string; i: number }) {
  const [abierta, setAbierta] = useState(false);
  return (
    <Revela retraso={i * 60} className="border-2 border-noche bg-white shadow-[4px_4px_0_0_#0A0147] dark:bg-zinc-900">
      <button type="button" onClick={() => setAbierta(!abierta)} aria-expanded={abierta}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left font-bold text-noche dark:text-white">
        {p}
        <span className={clsx("flex size-8 shrink-0 items-center justify-center border-2 border-noche font-titulo text-2xl text-noche transition-[transform,background-color] duration-300 ease-rebote", abierta ? "rotate-45 bg-coral" : "bg-menta")}>+</span>
      </button>
      <div className={clsx("grid transition-[grid-template-rows] duration-500 ease-salida", abierta ? "grid-rows-[1fr]" : "grid-rows-[0fr]")}>
        <div className="overflow-hidden px-5">
          <p className="pb-4 font-medium leading-relaxed text-zinc-600 dark:text-zinc-300">{r}</p>
        </div>
      </div>
    </Revela>
  );
}

/** Logotipo gigante del pie: cada letra sube con su retraso. */
function MarcaGigante() {
  const [ref, visto] = useVisible<HTMLDivElement>("0px 0px -5% 0px");
  return (
    <div ref={ref} aria-hidden className="flex select-none justify-center overflow-hidden pt-4 font-titulo text-[24vw] leading-[0.8] lg:text-[17rem]">
      {"HIREMIND".split("").map((l, i) => (
        <span key={i} className={clsx("inline-block transition-transform duration-[900ms] ease-rebote", i < 4 ? "text-white" : "text-menta", !visto && "translate-y-full")}
          style={{ transitionDelay: `${i * 55}ms` }}>{l}</span>
      ))}
    </div>
  );
}

/* ───────────────────────── página ───────────────────────── */

export default function Landing() {
  const [oculto, setOculto] = useState(false);

  useEffect(() => {
    // scroll suave con los mismos valores que la referencia (lerp 0.1)
    let id = 0;
    if (!sinMovimiento()) {
      lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
      const bucle = (t: number) => { lenis?.raf(t); id = requestAnimationFrame(bucle); };
      id = requestAnimationFrame(bucle);
    }
    // encabezado: se esconde al bajar y vuelve al subir
    let ultimo = window.scrollY;
    const alMover = () => {
      const y = window.scrollY;
      if (y > ultimo + 4 && y > 300) setOculto(true);
      else if (y < ultimo - 4) setOculto(false);
      ultimo = y;
    };
    window.addEventListener("scroll", alMover, { passive: true });
    return () => { cancelAnimationFrame(id); lenis?.destroy(); lenis = null; window.removeEventListener("scroll", alMover); };
  }, []);

  return (
    <div className="overflow-x-clip bg-white font-sans text-noche dark:bg-zinc-950 dark:text-white">
      <header className={clsx("fixed inset-x-3 top-3 z-40 transition-transform duration-500 ease-salida sm:inset-x-6", oculto && "-translate-y-[140%]")}>
        <div className="mx-auto flex max-w-6xl items-center gap-6 border-2 border-noche bg-white px-3 py-2 shadow-[4px_4px_0_0_#0A0147] sm:px-4 dark:bg-zinc-900">
          <button onClick={() => irA("inicio")} aria-label="Ir al inicio"><Logo animado /></button>
          <nav className="hidden gap-1 md:flex">
            {[["como", "Cómo funciona"], ["beneficios", "Beneficios"], ["planes", "Planes"], ["preguntas", "Preguntas"]].map(([id, t]) => (
              <button key={id} onClick={() => irA(id)}
                className="relative px-3 py-1.5 text-sm font-bold text-zinc-600 after:absolute after:inset-x-3 after:bottom-0.5 after:h-[3px] after:origin-left after:scale-x-0 after:bg-coral after:transition-transform after:duration-300 hover:text-noche hover:after:scale-x-100 dark:text-zinc-300 dark:hover:text-white">
                {t}
              </button>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-1.5">
            <BotonTema />
            <Link to="/app" className="btn-primario group py-1.5"><Etiqueta><span className="sm:hidden">App</span><span className="hidden sm:inline">Abrir la app</span></Etiqueta> <ArrowRight className="flecha size-4" /></Link>
          </div>
        </div>
      </header>

      {/* portada: el mismo lenguaje que la diapositiva de título del grupo */}
      <section id="inicio" className="relative overflow-hidden bg-menta pb-24 pt-32 text-noche lg:pb-32 lg:pt-40">
        <span aria-hidden className="absolute left-[38%] top-0 h-12 w-56 bg-noche" />
        <span aria-hidden className="absolute bottom-0 right-[18%] h-10 w-60 bg-noche" />
        <span aria-hidden className="absolute -bottom-24 -left-24 size-56 rounded-full border-[36px] border-coral" />
        <span aria-hidden className="absolute right-10 top-28 hidden h-4 w-32 bg-azul lg:block" />
        <div className="relative mx-auto grid max-w-6xl items-center gap-20 px-4 sm:px-6 lg:grid-cols-[1fr_1fr] lg:gap-16">
          <div>
            <span className="a-sube inline-flex items-center gap-2 border-2 border-noche bg-white px-3 py-1 text-xs font-extrabold uppercase italic tracking-wider">
              <Lock className="size-3.5" /> IA local · para PYMEs
            </span>
            <Palabras como="h1" texto="CONTRATE CON *CRITERIO.*" retraso={150} claseAcento="text-white [-webkit-text-stroke:2px_#0A0147] [paint-order:stroke_fill]"
              className="mt-6 font-titulo text-[22vw] leading-[0.85] sm:text-9xl lg:text-[6.4rem]" />
            <p className="a-sube mt-6 max-w-md text-xl font-semibold leading-snug" style={{ "--i": 8 } as CSSProperties}>
              Ranking de hojas de vida con evidencia. <span className="bg-white px-1">La IA ordena; usted decide.</span>
            </p>
            <div className="a-sube mt-8 flex flex-wrap gap-4" style={{ "--i": 10 } as CSSProperties}>
              <Link to="/app" className="btn-primario group px-6 py-3 text-base"><Etiqueta>Probar la demo</Etiqueta> <ArrowRight className="flecha size-5" /></Link>
              <button onClick={() => irA("como")} className="btn-secundario group px-6 py-3 text-base"><Etiqueta>Cómo funciona</Etiqueta></button>
            </div>
          </div>
          <div className="relative">
            <EscenaRanking />
            {/* cifras como etiquetas flotantes en vez de texto */}
            <span className="a-pop absolute -right-2 -top-7 z-10 rotate-3 border-2 border-noche bg-coral px-3 py-1.5 text-noche shadow-[4px_4px_0_0_#0A0147] sm:-right-6" style={{ "--i": 14 } as CSSProperties}>
              <span className="flota block"><b className="font-titulo text-3xl leading-none">~10 s</b> <span className="text-[11px] font-extrabold uppercase">por CV</span></span>
            </span>
            <span className="a-pop absolute -bottom-9 right-2 z-10 -rotate-3 border-2 border-noche bg-white px-3 py-1.5 text-noche shadow-[4px_4px_0_0_#0A0147]" style={{ "--i": 16 } as CSSProperties}>
              <span className="flota flex items-center gap-1.5 [animation-delay:-1.5s]"><Lock className="size-4" /><b className="font-titulo text-3xl leading-none">0</b><span className="text-[11px] font-extrabold uppercase leading-tight">datos<br />a la nube</span></span>
            </span>
          </div>
        </div>
      </section>

      <Cinta />

      {/* el problema */}
      <section className="relative bg-white dark:bg-zinc-950">
        <span aria-hidden className="absolute left-[30%] top-0 h-4 w-40 bg-azul" />
        <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
          <Palabras texto="MUCHOS POSTULANTES, *POCO TIEMPO* Y CRITERIOS QUE CAMBIAN" className="max-w-4xl font-titulo text-5xl text-noche sm:text-7xl dark:text-white" />
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {[
              ["Decenas de CV por vacante", "Cada oferta publicada en portales de empleo llena la bandeja de entrada en pocos días.", "bg-coral"],
              ["Horas de lectura manual", "En una PYME, quien selecciona también hace otras tareas. Leer todo con calma no siempre es posible.", "bg-azul"],
              ["Criterios que se mueven", "Al cansarse, se compara distinto el primer CV y el último, y se cuelan datos irrelevantes como la edad.", "bg-ambar"],
            ].map(([t, d, c], i) => (
              <Revela key={t} retraso={i * 120} className="relative border-2 border-noche bg-white p-6 shadow-[6px_6px_0_0_#0A0147] transition-transform duration-300 ease-rebote hover:-translate-y-1 dark:bg-zinc-900">
                <span className={clsx("absolute -top-3 left-6 h-6 w-14 border-2 border-noche", c)} />
                <h3 className="mt-2 font-titulo text-3xl text-noche dark:text-white">{t}</h3>
                <p className="mt-2 font-medium leading-relaxed text-zinc-600 dark:text-zinc-300">{d}</p>
              </Revela>
            ))}
          </div>
        </div>
      </section>

      <ComoFunciona />

      {/* beneficios sobre coral, como la diapositiva del problema */}
      <section id="beneficios" className="relative overflow-hidden bg-coral text-noche">
        <span aria-hidden className="absolute -right-16 -top-16 size-48 rounded-full border-[30px] border-noche" />
        <span aria-hidden className="absolute bottom-0 left-0 h-12 w-72 bg-noche" />
        <div className="relative mx-auto max-w-6xl px-4 py-24 sm:px-6">
          <p className="text-sm font-extrabold uppercase italic tracking-wider">Beneficios</p>
          <Palabras texto="RÁPIDO PARA USTED, *JUSTO* PARA QUIEN POSTULA" claseAcento="text-white [-webkit-text-stroke:2px_#0A0147] [paint-order:stroke_fill]" className="mt-2 max-w-3xl font-titulo text-5xl sm:text-7xl" />
          <Pops className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {BENEFICIOS.map((b) => (
              <div key={b.t} className="group h-full border-2 border-noche bg-white p-6 shadow-[6px_6px_0_0_#0A0147] transition-[transform,box-shadow] duration-200 ease-rebote hover:-translate-x-1 hover:-translate-y-1 hover:shadow-[10px_10px_0_0_#0A0147] dark:bg-zinc-900 dark:text-white">
                <span className={clsx("flex size-12 items-center justify-center border-2 border-noche text-noche transition-transform duration-300 ease-rebote group-hover:-rotate-6 group-hover:scale-110", b.c)}>
                  <b.i className="size-6" />
                </span>
                <h3 className="mt-5 font-titulo text-3xl">{b.t}</h3>
                <p className="mt-1.5 font-medium leading-relaxed text-zinc-600 dark:text-zinc-300">{b.d}</p>
              </div>
            ))}
          </Pops>
        </div>
      </section>

      <Planes />

      <section id="preguntas" className="relative bg-white dark:bg-zinc-950">
        <span aria-hidden className="absolute right-[25%] top-0 h-4 w-40 bg-azul" />
        <div className="mx-auto max-w-3xl px-4 py-24 sm:px-6">
          <Palabras texto="PREGUNTAS *FRECUENTES*" className="text-center font-titulo text-5xl text-noche sm:text-7xl dark:text-white" />
          <div className="mt-12 space-y-4">
            {PREGUNTAS.map(([p, r], i) => <Pregunta key={p} p={p} r={r} i={i} />)}
          </div>
        </div>
      </section>

      <footer className="relative overflow-hidden bg-noche text-white">
        <span aria-hidden className="absolute left-[15%] top-0 h-4 w-48 bg-menta" />
        <div className="mx-auto flex max-w-6xl flex-col items-start gap-8 px-4 pb-16 pt-24 sm:px-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Palabras texto="SU PRÓXIMA VACANTE, *REVISADA CON EVIDENCIA.*" claseAcento="text-menta" className="max-w-3xl font-titulo text-5xl sm:text-7xl" />
            <Revela retraso={300}><p className="mt-4 max-w-xl text-lg font-medium text-white/80">Pruébelo con las 2 vacantes y los 15 CV de ejemplo incluidos. Funciona en una PC de oficina con 16 GB de RAM.</p></Revela>
          </div>
          <Revela retraso={450}>
            <Link to="/app" className="btn-primario group border-white px-7 py-4 text-lg shadow-[5px_5px_0_0_#2EE5A7] hover:shadow-[7px_7px_0_0_#2EE5A7]">
              <Etiqueta>Probar la demo</Etiqueta> <ArrowRight className="flecha size-5" />
            </Link>
          </Revela>
        </div>
        <MarcaGigante />
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 border-t-2 border-white/15 px-4 py-6 text-center text-xs font-semibold text-white/70 sm:flex-row sm:px-6 sm:text-left">
          <span className="flex items-center gap-2"><Simbolo className="size-6" /> HireMind · La IA ordena; una persona decide.</span>
          <p>Proyecto de Inteligencia Artificial · Escuela Politécnica Nacional · 2026</p>
        </div>
      </footer>
    </div>
  );
}
