// Página de venta. Hoy vive dentro de la app; está pensada para separarse a su propio sitio.
import {
  ArrowRight, BadgeCheck, Clock, Download, EyeOff, FileUp, ListChecks, Lock, Quote, ScanLine, ShieldCheck, Star, Trophy, UserCheck,
} from "lucide-react";
import type { ReactNode } from "react";
import { Link } from "react-router";
import { BotonTema, Logo, PuntoEstado } from "../components/ui";

function Vista() {
  const filas = [
    { n: "Andrea Salazar", p: 100, e: ["cumple", "cumple", "cumple", "cumple", "cumple"] },
    { n: "Carlos Ortiz", p: 90, e: ["cumple", "cumple", "cumple", "cumple", "no_identificado"] },
    { n: "Daniela Mora", p: 90, e: ["cumple", "cumple", "cumple", "cumple", "no_identificado"] },
    { n: "Luis Andrango", p: 57.5, e: ["parcial", "parcial", "cumple", "no_identificado", "cumple"] },
  ] as const;
  return (
    <div className="relative">
      <div className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-to-tr from-marca-200/60 via-sky-100/40 to-transparent blur-2xl dark:from-marca-900/40 dark:via-sky-950/30" />
      <div className="tarjeta overflow-hidden shadow-xl shadow-marca-900/5">
        <div className="flex items-center gap-1.5 border-b border-zinc-200 px-4 py-2.5 dark:border-zinc-800">
          <span className="size-2.5 rounded-full bg-zinc-200 dark:bg-zinc-700" /><span className="size-2.5 rounded-full bg-zinc-200 dark:bg-zinc-700" /><span className="size-2.5 rounded-full bg-zinc-200 dark:bg-zinc-700" />
          <span className="ml-3 text-xs text-zinc-500">Asistente contable · Ranking</span>
        </div>
        <ul className="divide-y divide-zinc-100 dark:divide-zinc-800">
          {filas.map((f, i) => (
            <li key={f.n} className={`flex items-center gap-3 px-4 py-3 ${i === 0 ? "bg-marca-50/70 dark:bg-marca-950/40" : ""}`}>
              <span className="flex size-6 items-center justify-center rounded-full bg-marca-600 text-[11px] font-semibold text-white">{i + 1}</span>
              <div className="flex-1">
                <p className="flex items-center gap-1 text-sm font-medium">{f.n} <Star className="size-3 fill-amber-400 text-amber-400" /></p>
                <div className="mt-1 flex gap-1">{f.e.map((e, j) => <PuntoEstado key={j} estado={e} titulo="" />)}</div>
              </div>
              <span className="text-sm font-semibold tabular-nums">{String(f.p).replace(".", ",")}</span>
            </li>
          ))}
        </ul>
        <div className="border-t border-zinc-200 p-4 dark:border-zinc-800">
          <p className="text-[11px] font-medium uppercase tracking-wider text-zinc-400">Evidencia · Facturación electrónica / SRI</p>
          <blockquote className="mt-2 flex gap-2 rounded-lg bg-zinc-50 px-3 py-2 text-xs text-zinc-700 ring-1 ring-inset ring-zinc-200/70 dark:bg-zinc-800/50 dark:text-zinc-300 dark:ring-zinc-800">
            <Quote className="mt-0.5 size-3 shrink-0 text-zinc-400" />
            <span className="flex-1">Facturación electrónica SRI</span>
            <BadgeCheck className="size-3.5 shrink-0 text-emerald-500" />
          </blockquote>
        </div>
      </div>
    </div>
  );
}

function Beneficio({ icono, titulo, texto }: { icono: ReactNode; titulo: string; texto: string }) {
  return (
    <div className="tarjeta p-5">
      <div className="flex size-9 items-center justify-center rounded-lg bg-marca-50 text-marca-600 dark:bg-marca-950 dark:text-marca-300">{icono}</div>
      <h3 className="mt-4 font-semibold">{titulo}</h3>
      <p className="mt-1.5 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">{texto}</p>
    </div>
  );
}

const PASOS = [
  { i: <ListChecks className="size-5" />, t: "Defina la vacante", d: "Criterios de formación, experiencia, habilidades e idiomas, con su peso." },
  { i: <FileUp className="size-5" />, t: "Suba los PDF", d: "Arrastre todas las hojas de vida. Los escaneados se separan para revisión manual." },
  { i: <ShieldCheck className="size-5" />, t: "El agente verifica", d: "Extrae cada dato con una cita del CV; si la cita no existe, el dato no cuenta." },
  { i: <Trophy className="size-5" />, t: "Usted decide", d: "Ranking justificado con evidencias. Revise el top 5 y corrija si hace falta." },
];

const PREGUNTAS = [
  ["¿Necesito internet o una cuenta en la nube?", "No. El modelo de lenguaje corre en el mismo computador con LM Studio. Las hojas de vida nunca salen de su oficina."],
  ["¿La IA decide a quién contratar?", "No. Ordena y justifica con evidencias. Ningún CV se descarta automáticamente y la decisión final es siempre de una persona."],
  ["¿Qué pasa si la IA se equivoca?", "Cada dato tiene una cita del CV que usted puede leer. Si un criterio está mal evaluado, lo corrige con un clic y el puntaje se recalcula."],
  ["¿Qué computador necesito?", "Una PC de oficina con 16 GB de RAM. Con tarjeta gráfica cada CV tarda alrededor de 10 segundos."],
  ["¿Cómo se evita la discriminación?", "La edad, el estado civil, la nacionalidad y otros datos personales se eliminan antes del análisis, y no se permiten criterios sobre ellos."],
];

export default function Landing() {
  return (
    <div className="bg-white dark:bg-zinc-950">
      <header className="sticky top-0 z-30 border-b border-zinc-200/70 bg-white/80 backdrop-blur dark:border-zinc-800/70 dark:bg-zinc-950/80">
        <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 sm:px-6">
          <Logo />
          <nav className="hidden gap-6 text-sm text-zinc-600 md:flex dark:text-zinc-400">
            <a href="#como" className="hover:text-zinc-900 dark:hover:text-white">Cómo funciona</a>
            <a href="#beneficios" className="hover:text-zinc-900 dark:hover:text-white">Beneficios</a>
            <a href="#preguntas" className="hover:text-zinc-900 dark:hover:text-white">Preguntas</a>
          </nav>
          <div className="ml-auto flex items-center gap-1">
            <BotonTema />
            <Link to="/app" className="btn-primario py-1.5">Abrir la app <ArrowRight className="size-4" /></Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-6xl items-center gap-12 px-4 pb-20 pt-16 sm:px-6 lg:grid-cols-2 lg:pt-24">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-marca-200 bg-marca-50 px-3 py-1 text-xs font-medium text-marca-700 dark:border-marca-900 dark:bg-marca-950 dark:text-marca-300">
            <Lock className="size-3" /> IA local · para PYMEs ecuatorianas
          </span>
          <h1 className="mt-5 text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
            Preseleccione hojas de vida en minutos, <span className="text-marca-600 dark:text-marca-400">sin que salgan de su oficina.</span>
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-pretty text-zinc-600 dark:text-zinc-400">
            HireMind lee los CV, los compara con su vacante y entrega un ranking justificado con citas del propio documento.
            La IA ordena; usted decide.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/app" className="btn-primario px-5 py-2.5">Probar la demo <ArrowRight className="size-4" /></Link>
            <a href="#como" className="btn-secundario px-5 py-2.5">Cómo funciona</a>
          </div>
          <dl className="mt-10 grid max-w-md grid-cols-3 gap-6 border-t border-zinc-200 pt-6 dark:border-zinc-800">
            {[["~10 s", "por hoja de vida"], ["0", "datos en la nube"], ["100 %", "puntajes con evidencia"]].map(([v, t]) => (
              <div key={t}><dt className="text-2xl font-semibold tabular-nums">{v}</dt><dd className="mt-0.5 text-xs text-zinc-500">{t}</dd></div>
            ))}
          </dl>
        </div>
        <Vista />
      </section>

      <section className="border-y border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900/40">
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-14 sm:px-6 md:grid-cols-3">
          {[
            ["Decenas de CV por vacante", "Cada oferta publicada en portales de empleo llena la bandeja de entrada en pocos días."],
            ["Horas de lectura manual", "En una PYME, quien selecciona también hace otras tareas. Leer todo con calma no siempre es posible."],
            ["Criterios que cambian", "Al cansarse, se compara distinto al primer CV y al último, y se cuelan datos irrelevantes como la edad."],
          ].map(([t, d]) => (
            <div key={t}>
              <h3 className="font-semibold">{t}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">{d}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="como" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-20 sm:px-6">
        <p className="text-sm font-medium text-marca-600 dark:text-marca-400">Cómo funciona</p>
        <h2 className="mt-2 max-w-2xl text-3xl font-semibold tracking-tight text-balance">De una carpeta de PDF a un ranking que puede explicar</h2>
        <ol className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {PASOS.map((p, i) => (
            <li key={p.t} className="relative">
              <div className="flex items-center gap-3">
                <div className="flex size-10 items-center justify-center rounded-xl bg-marca-600 text-white shadow-sm shadow-marca-600/30">{p.i}</div>
                <span className="text-xs font-medium tabular-nums text-zinc-400">Paso {i + 1}</span>
              </div>
              <h3 className="mt-4 font-semibold">{p.t}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">{p.d}</p>
            </li>
          ))}
        </ol>
      </section>

      <section id="beneficios" className="scroll-mt-20 bg-zinc-50 dark:bg-zinc-900/40">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <p className="text-sm font-medium text-marca-600 dark:text-marca-400">Beneficios</p>
          <h2 className="mt-2 max-w-2xl text-3xl font-semibold tracking-tight text-balance">Rápido para usted, justo para quien postula</h2>
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Beneficio icono={<Lock className="size-5" />} titulo="100 % local" texto="El modelo corre en su computador. Cumple con la protección de datos personales sin depender de la nube." />
            <Beneficio icono={<Quote className="size-5" />} titulo="Cada dato con su cita" texto="El agente copia la frase del CV que respalda cada dato. Si la frase no existe, el dato no suma puntos." />
            <Beneficio icono={<EyeOff className="size-5" />} titulo="Equidad desde el inicio" texto="Edad, estado civil, nacionalidad y otros datos personales se quitan antes de que el modelo lea el CV." />
            <Beneficio icono={<UserCheck className="size-5" />} titulo="Una persona decide" texto="No se descarta a nadie de forma automática. El ranking es una ayuda; la decisión es suya." />
            <Beneficio icono={<ScanLine className="size-5" />} titulo="Sin sorpresas" texto="Los PDF escaneados o ilegibles se separan para revisión manual en lugar de recibir un puntaje inventado." />
            <Beneficio icono={<Download className="size-5" />} titulo="Corrija y exporte" texto="Ajuste cualquier criterio con un clic y descargue el ranking en CSV para compartirlo con su equipo." />
          </div>
        </div>
      </section>

      <section id="preguntas" className="mx-auto max-w-3xl scroll-mt-20 px-4 py-20 sm:px-6">
        <h2 className="text-center text-3xl font-semibold tracking-tight">Preguntas frecuentes</h2>
        <div className="mt-10 divide-y divide-zinc-200 dark:divide-zinc-800">
          {PREGUNTAS.map(([p, r]) => (
            <details key={p} className="group py-4">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium">
                {p}
                <span className="text-zinc-400 transition group-open:rotate-45">+</span>
              </summary>
              <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">{r}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="px-4 pb-20 sm:px-6">
        <div className="mx-auto max-w-6xl overflow-hidden rounded-2xl bg-marca-600 px-6 py-14 text-center text-white sm:px-12">
          <h2 className="text-3xl font-semibold tracking-tight text-balance">Su próxima vacante, revisada con evidencia</h2>
          <p className="mx-auto mt-3 max-w-xl text-marca-100">Pruebe HireMind con las 2 vacantes y los 15 CV de ejemplo incluidos.</p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link to="/app" className="btn bg-white px-5 py-2.5 text-marca-700 hover:bg-marca-50">Probar la demo <ArrowRight className="size-4" /></Link>
          </div>
          <p className="mt-6 flex items-center justify-center gap-1.5 text-xs text-marca-200"><Clock className="size-3.5" /> Funciona en una PC de oficina con 16 GB de RAM</p>
        </div>
      </section>

      <footer className="border-t border-zinc-200 dark:border-zinc-800">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-4 py-6 text-xs text-zinc-500 sm:flex-row sm:px-6">
          <Logo className="text-sm text-zinc-700 dark:text-zinc-300" />
          <p>Proyecto de Inteligencia Artificial · Escuela Politécnica Nacional · 2026</p>
        </div>
      </footer>
    </div>
  );
}
