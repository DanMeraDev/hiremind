"""Prepara y arranca HireMind para la demo con varios usuarios a la vez.

    python demo.py              # revisa todo, carga el modelo para 3 usuarios y abre la app a la red
    python demo.py --revisar    # solo revisa, no arranca nada (útil la noche anterior)
    python demo.py --local      # solo en esta PC (sin otros dispositivos)
    python demo.py -u 1         # modelo para 1 usuario (menos RAM)

Funciona en Linux, Windows y macOS. Solo usa la biblioteca estándar: si falta el entorno
.venv lo crea e instala requirements.txt. La guía completa está en DEMO.md.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
WIN = os.name == "nt"
VENV_PY = RAIZ / ".venv" / ("Scripts/python.exe" if WIN else "bin/python")
MODELO = os.getenv("HIREMIND_MODELO", "qwen/qwen3-4b-2507")
CTX_POR_USUARIO = 8192
problemas: list[str] = []


def ok(t): print(f"  [ok] {t}")
def aviso(t): print(f"  [!]  {t}")


def falla(t, como=""):
    print(f"  [X]  {t}" + (f"\n       → {como}" if como else ""))
    problemas.append(t)


def paso(t): print(f"\n== {t}")


def correr(cmd, **k) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **k)


# ------------------------------------------------------------------ entorno
def revisar_python():
    paso("Python")
    v = sys.version_info
    if v < (3, 10):
        falla(f"Python {v.major}.{v.minor} es muy viejo", "instale Python 3.12 y corra: python3.12 demo.py")
        return
    ok(f"Python {v.major}.{v.minor}")
    req = RAIZ / "requirements.txt"
    marca = RAIZ / ".venv" / ".requirements.sha"
    huella = hashlib.sha256(req.read_bytes()).hexdigest()
    if not VENV_PY.exists():
        print("  Creando .venv (solo la primera vez)…")
        subprocess.run([sys.executable, "-m", "venv", str(RAIZ / ".venv")], check=True)
    if not marca.exists() or marca.read_text().strip() != huella:
        print("  Instalando dependencias de Python (1–3 min la primera vez)…")
        if correr([str(VENV_PY), "-m", "pip", "--version"]).returncode:
            correr([str(VENV_PY), "-m", "ensurepip", "--upgrade"])  # .venv creado sin pip (p. ej. con uv)
        if correr([str(VENV_PY), "-m", "pip", "--version"]).returncode == 0:
            r = subprocess.run([str(VENV_PY), "-m", "pip", "install", "-q", "--disable-pip-version-check", "-r", str(req)])
        elif uv := shutil.which("uv"):
            r = subprocess.run([uv, "pip", "install", "-q", "--python", str(VENV_PY), "-r", str(req)])
        else:
            falla(".venv no tiene pip", "borre la carpeta .venv y vuelva a correr demo.py")
            return
        if r.returncode:
            falla("pip no pudo instalar requirements.txt", "revise la conexión a internet y vuelva a correr demo.py")
            return
        marca.write_text(huella)
    ok("dependencias de Python instaladas en .venv")


def revisar_web():
    paso("Interfaz web")
    web, dist = RAIZ / "web", RAIZ / "web" / "dist" / "index.html"
    fuentes = [p for p in (web / "src").rglob("*") if p.is_file()] + [web / "index.html", web / "package.json"]
    desactualizada = not dist.exists() or max(p.stat().st_mtime for p in fuentes) > dist.stat().st_mtime
    if not desactualizada:
        ok("interfaz compilada (web/dist)")
        return
    npm = shutil.which("npm")
    if not npm:
        falla("falta compilar la interfaz y no está Node.js", "instale Node.js 20+ (nodejs.org) y vuelva a correr demo.py")
        return
    print("  Compilando la interfaz (1–2 min)…")
    if not (web / "node_modules").exists() and subprocess.run([npm, "install"], cwd=web).returncode:
        falla("npm install falló", "revise la conexión a internet")
        return
    if subprocess.run([npm, "run", "build"], cwd=web).returncode:
        falla("npm run build falló", "corra 'cd web && npm run build' para ver el error")
        return
    ok("interfaz compilada")


def ram_gb() -> float:
    try:
        if WIN:
            class M(ctypes.Structure):
                _fields_ = [("l", ctypes.c_ulong), ("c", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in "abcdefg"]
            m = M(); m.l = ctypes.sizeof(M)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.a / 1e9
        if platform.system() == "Darwin":
            return int(correr(["sysctl", "-n", "hw.memsize"]).stdout) / 1e9
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9
    except Exception:
        return 0.0


def revisar_ram(usuarios: int):
    paso("Memoria")
    gb = ram_gb()
    if not gb:
        aviso("no pude medir la RAM")
    elif usuarios >= 3 and gb < 15:
        falla(f"{gb:.0f} GB de RAM es poco para {usuarios} usuarios", "use 'python demo.py -u 1' o una laptop de 16 GB")
    else:
        ok(f"{gb:.0f} GB de RAM")
    if usuarios >= 3:
        aviso("cierre Chrome con muchas pestañas, Discord, Teams, etc.: con 3 usuarios se usan ~14 GB en total")


# ------------------------------------------------------------------ LM Studio
def buscar_lms() -> str | None:
    if p := shutil.which("lms"):
        return p
    p = Path.home() / ".lmstudio" / "bin" / ("lms.exe" if WIN else "lms")
    return str(p) if p.exists() else None


def lms_json(lms, *args):
    r = correr([lms, *args, "--json"])
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return []


def revisar_modelo(usuarios: int):
    paso(f"LM Studio · {MODELO} para {usuarios} usuario(s)")
    lms = buscar_lms()
    if not lms:
        falla("no encuentro el comando 'lms'",
              "abra LM Studio una vez (instala 'lms'), o en Configuración > Developer active el CLI; luego cierre y abra la terminal")
        return
    if not any(m.get("modelKey") == MODELO for m in lms_json(lms, "ls")):
        falla(f"el modelo {MODELO} no está descargado", f"corra: lms get {MODELO}   (≈2,5 GB, hágalo en casa)")
        return
    ok("modelo descargado")
    r = correr([lms, "server", "start"])
    if r.returncode:
        falla("no pude iniciar el servidor de LM Studio", "abra la app LM Studio y vuelva a correr demo.py\n       " + (r.stderr or r.stdout).strip()[:200])
        return
    cargado = [m for m in lms_json(lms, "ps") if m.get("modelKey") == MODELO]
    if cargado and (cargado[0].get("parallel") or 1) >= usuarios:
        ok(f"modelo ya cargado con {cargado[0].get('parallel')} usuarios en paralelo")
    else:
        for m in cargado:
            correr([lms, "unload", m["identifier"]])
        print(f"  Cargando el modelo para {usuarios} usuarios (≈30 s)…")
        r = correr([lms, "load", MODELO, "--parallel", str(usuarios), "-c", str(CTX_POR_USUARIO * usuarios),
                    "--identifier", MODELO, "-y"])
        if r.returncode:
            falla("lms load falló", (r.stderr or r.stdout).strip()[-300:])
            return
        ok(f"modelo cargado: {usuarios} en paralelo, contexto {CTX_POR_USUARIO * usuarios}")
    try:
        with urllib.request.urlopen("http://localhost:1234/v1/models", timeout=5) as resp:
            ids = [m["id"] for m in json.load(resp)["data"]]
        ok("LM Studio responde en http://localhost:1234") if MODELO in ids else falla(f"LM Studio responde pero sin {MODELO}")
    except Exception as e:
        falla(f"LM Studio no responde en el puerto 1234 ({type(e).__name__})")


# ------------------------------------------------------------------ datos y red
def revisar_datos():
    paso("Datos")
    if (RAIZ / ".env").exists():
        ok(".env presente: el correo al candidato se puede enviar")
    else:
        aviso("no hay .env: la selección funciona pero NO envía correo (copie .env.example como .env)")
    db = RAIZ / os.getenv("HIREMIND_DB", "hiremind.db")
    usuarios: list[tuple[str, int]] = []
    if db.exists():
        try:
            with sqlite3.connect(db) as con:
                usuarios = con.execute("SELECT u.usuario, COUNT(v.id) FROM usuarios u "
                                       "LEFT JOIN vacantes v ON v.usuario_id=u.id GROUP BY u.id ORDER BY u.usuario").fetchall()
        except sqlite3.Error:  # base sin tabla usuarios (de antes del inicio de sesión)
            pass
    if usuarios:
        ok("usuarios: " + ", ".join(f"{u} ({n} vacante{'s' if n != 1 else ''})" for u, n in usuarios))
    else:
        falla("no hay usuarios para iniciar sesión",
              "corra: python demo.py --vacantes (crea usuario1-3, contraseña hiremind, con sus vacantes)")


def _es_virtual(ip: str) -> bool:
    """Docker (172.17–31.x) y VPN tipo Tailscale (100.64–127.x): no sirven para los celulares."""
    a, b = (int(x) for x in ip.split(".")[:2])
    return ip.startswith("127.") or (a == 172 and 17 <= b <= 31) or (a == 100 and 64 <= b <= 127)


def ips_locales() -> list[str]:
    for destino in ("8.8.8.8", "192.168.1.1", "10.0.0.1"):  # UDP connect no envía nada: solo elige la interfaz
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect((destino, 80))
                ip = s.getsockname()[0]
            if not _es_virtual(ip):
                return [ip]
        except OSError:
            pass
    try:
        todas = {i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)}
    except OSError:
        todas = set()
    return sorted(i for i in todas if not _es_virtual(i))


def revisar_red(puerto: int, local: bool) -> list[str]:
    paso("Red")
    if local:
        ok("modo local: solo esta PC")
        return []
    ips = ips_locales()
    if not ips:
        falla("no hay red", "conéctese al WiFi o al hotspot del celular ANTES de arrancar")
    else:
        ok("IP en la red: " + ", ".join(ips))
    if WIN:
        aviso("la primera vez Windows pregunta por el firewall: marque 'Redes privadas' y acepte")
        aviso("si usa el hotspot de un celular, en Windows póngalo como red PRIVADA (Configuración > Red)")
    elif shutil.which("firewall-cmd") and correr(["firewall-cmd", "--state"]).returncode == 0:
        if correr(["firewall-cmd", f"--query-port={puerto}/tcp"]).stdout.strip() != "yes":
            aviso(f"el firewall bloquea el puerto {puerto}. Ábralo mientras dure la demo:\n"
                  f"       sudo firewall-cmd --add-port={puerto}/tcp      (se borra al reiniciar)")
    elif shutil.which("ufw") and "active" in correr(["ufw", "status"]).stdout:
        aviso(f"ufw está activo: sudo ufw allow {puerto}/tcp")
    return ips


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-u", "--usuarios", type=int, default=3, help="usuarios simultáneos (por defecto 3)")
    ap.add_argument("-p", "--puerto", type=int, default=int(os.getenv("PUERTO", 8000)))
    ap.add_argument("--revisar", action="store_true", help="solo revisar, no arrancar")
    ap.add_argument("--local", action="store_true", help="no abrir a la red")
    ap.add_argument("--vacantes", action="store_true", help="crear los 3 usuarios de prueba y sus vacantes si no existen")
    a = ap.parse_args()
    os.chdir(RAIZ)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows
    except AttributeError:
        pass
    print("HireMind · preparación de la demo")

    revisar_python()
    revisar_web()
    revisar_ram(a.usuarios)
    revisar_modelo(a.usuarios)
    if a.vacantes and VENV_PY.exists():
        subprocess.run([str(VENV_PY), "scripts/cargar_seeds.py", "--sin-evaluar"])
    revisar_datos()
    ips = revisar_red(a.puerto, a.local)

    if problemas:
        print(f"\n{len(problemas)} problema(s) por resolver antes de la demo (ver [X] arriba).")
        sys.exit(1)
    if a.revisar:
        print("\nTodo listo. Para arrancar: python demo.py")
        return

    host = "127.0.0.1" if a.local else "0.0.0.0"
    print("\n" + "=" * 60)
    print(f"  En esta PC:          http://localhost:{a.puerto}")
    for ip in ips:
        print(f"  Otros dispositivos:  http://{ip}:{a.puerto}")
    print("  (mismo WiFi u hotspot) · Ctrl+C para detener")
    print("=" * 60 + "\n", flush=True)
    proc = subprocess.Popen([str(VENV_PY), "-m", "uvicorn", "api.main:app", "--host", host, "--port", str(a.puerto)])
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        time.sleep(1)
        print("\nHireMind detenido. La app ya no está abierta a la red.")


if __name__ == "__main__":
    main()
