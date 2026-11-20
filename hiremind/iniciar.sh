#!/usr/bin/env bash
# Arranca HireMind: compila la interfaz (si hace falta) y levanta la API en http://localhost:8000
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d web/dist ] || [ -n "$(find web/src web/index.html -newer web/dist/index.html 2>/dev/null | head -1)" ]; then
  echo "Compilando la interfaz…"
  (cd web && { [ -d node_modules ] || npm install; } && npm run build)
fi
echo "HireMind en http://localhost:8000"
exec .venv/bin/uvicorn api.main:app --host 127.0.0.1 --port "${PUERTO:-8000}"
