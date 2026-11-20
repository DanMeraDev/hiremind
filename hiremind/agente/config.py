"""Configuración del agente. Todo se puede cambiar con variables de entorno."""
import os

# Servidor local de LM Studio (API compatible con OpenAI)
LLM_URL = os.getenv("HIREMIND_LLM_URL", "http://localhost:1234/v1")
MODELO = os.getenv("HIREMIND_MODELO", "qwen/qwen3-4b-2507")

DB_PATH = os.getenv("HIREMIND_DB", "hiremind.db")
# Copia de los PDF subidos (para abrir el original desde la interfaz)
ARCHIVOS_DIR = os.getenv("HIREMIND_ARCHIVOS", "archivos")

# Un PDF con menos caracteres que esto se considera escaneado/ilegible -> revisión manual
MIN_CARACTERES = 200
# Reintentos si el JSON del modelo no es válido (después: revisión manual)
MAX_REINTENTOS = 2
# Similitud mínima (0-100) para aceptar una cita larga que no aparece exacta en el CV
UMBRAL_CITA = 90
# Cantidad de candidatos que la persona revisa
TOP_N = 5
# Texto máximo del CV que se envía al modelo (caracteres)
MAX_CHARS_CV = 12000
