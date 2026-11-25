import { useMutation, useQueryClient } from "@tanstack/react-query";
import { LogIn } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router";
import { api } from "../api";
import { Aviso, BotonTema, Logo } from "../components/ui";

export default function Login() {
  const [usuario, setUsuario] = useState("");
  const [clave, setClave] = useState("");
  const qc = useQueryClient();
  const navegar = useNavigate();
  const volver = useSearchParams()[0].get("volver");
  const entrar = useMutation({
    mutationFn: () => api.login(usuario, clave),
    onSuccess: (u) => {
      qc.clear(); // nada del usuario anterior en caché
      qc.setQueryData(["yo"], u);
      navegar(volver?.startsWith("/app") ? volver : "/app", { replace: true });
    },
  });
  const enviar = (e: FormEvent) => {
    e.preventDefault();
    entrar.mutate();
  };

  return (
    <div className="relative flex min-h-dvh items-center justify-center bg-zinc-50 px-4 py-10 dark:bg-zinc-950">
      <span aria-hidden className="pointer-events-none absolute right-6 top-0 hidden h-3 w-44 bg-azul sm:block" />
      <div className="absolute right-4 top-4"><BotonTema /></div>
      <form onSubmit={enviar} className="tarjeta a-sube w-full max-w-sm space-y-5 p-6 sm:p-8">
        <Link to="/" className="inline-block"><Logo /></Link>
        <div>
          <h1 className="font-titulo text-4xl">INICIAR SESIÓN</h1>
          <p className="mt-1 text-sm text-zinc-500">Cada reclutador ve solo sus vacantes y candidatos.</p>
        </div>
        <label className="block">
          <span className="etiqueta">Usuario</span>
          <input className="campo" autoFocus autoComplete="username" autoCapitalize="none" value={usuario}
            onChange={(e) => setUsuario(e.target.value)} placeholder="usuario1" required />
        </label>
        <label className="block">
          <span className="etiqueta">Contraseña</span>
          <input className="campo" type="password" autoComplete="current-password" value={clave}
            onChange={(e) => setClave(e.target.value)} required />
        </label>
        {entrar.error && <Aviso>{entrar.error.message}</Aviso>}
        <button className="btn-primario w-full" disabled={entrar.isPending || !usuario || !clave}>
          <LogIn className="size-4" /> {entrar.isPending ? "Entrando…" : "Entrar"}
        </button>
        <p className="border-t-2 border-dashed border-zinc-200 pt-4 text-xs leading-relaxed text-zinc-500 dark:border-zinc-700">
          Demo: <strong className="text-noche dark:text-zinc-200">usuario1</strong>, <strong className="text-noche dark:text-zinc-200">usuario2</strong> o{" "}
          <strong className="text-noche dark:text-zinc-200">usuario3</strong> · contraseña <strong className="text-noche dark:text-zinc-200">hiremind</strong>
        </p>
      </form>
    </div>
  );
}
