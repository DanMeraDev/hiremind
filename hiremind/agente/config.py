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


# ---------------------------------------------------------------- correo (SMTP)
def _cargar_env(ruta: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")) -> None:
    """Lee hiremind/.env (CLAVE=valor) sin pisar variables ya definidas. El archivo no se sube a git."""
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


_cargar_env()

MAIL_HOST = os.getenv("MAIL_HOST", "")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_SMTP_AUTH = os.getenv("MAIL_SMTP_AUTH", "true").lower() == "true"
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "true").lower() == "true"
MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)
# Modo prueba: si tiene un correo, TODOS los envíos van a esa dirección (el asunto indica el destinatario original)
MAIL_REDIRIGIR_A = os.getenv("MAIL_REDIRIGIR_A", "").strip()
