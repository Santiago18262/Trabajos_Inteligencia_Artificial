
# Configuraciones de expresiones regulares

import re  # Importa el módulo estándar para trabajar con expresiones regulares en Python

# --- Detecta URLs (enlaces) ---
URL_RE = re.compile(
    r"(https?://[^\s]+)",  # Busca cadenas que empiecen con http:// o https:// seguidas de cualquier carácter no espacio
    re.IGNORECASE          # Ignora mayúsculas/minúsculas al comparar (por ejemplo, HTTP o http)
)

# --- Detecta nombres de archivos adjuntos en texto ---
ADJUNTO_RE = re.compile(
    r"(?<!\S)"  # Asegura que antes no haya un carácter no-espacio (inicio de palabra o después de un espacio)
    r"(?P<name>(?:[\w\-\(\)\[\]&]+(?:[ \t]+[\w\-\(\)\[\]&]+)*)\."  # Captura el nombre del archivo antes del punto
    r"(?P<ext>[A-Za-z0-9]{1,6}))"  # Captura la extensión (1 a 6 letras/números)
    r"(?=$|[\s\)\]\.,;:!?])",  # Asegura que después venga un espacio, puntuación o final del texto
    re.UNICODE  # Soporta caracteres Unicode en los nombres
)

# --- Conjuntos de extensiones de archivos ---
EXT_PELIGROSAS = {  # Extensiones asociadas a ejecutables o scripts peligrosos
    "exe", "bat", "cmd", "js", "vbs", "scr", "msi", "jar",
    "iso", "lnk", "ps1", "apk", "reg"
}

EXT_COMUNES = {  # Extensiones típicas de documentos y archivos comprimidos
    "zip", "rar", "7z", "pdf", "doc", "docx", "docm",
    "xls", "xlsx", "xlsm", "ppt", "pptx", "pptm",
    "csv", "txt"
}

# --- Validación básica de correos electrónicos ---
EMAIL_RE = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$",  # Patrón: algo@algo.algo sin espacios
)
def es_email_valido(s: str) -> bool:
    """Devuelve True si el correo tiene un formato válido (mínimo algo@algo.algo)."""
    return bool(EMAIL_RE.match((s or "").strip()))  # Limpia espacios y verifica coincidencia con el patrón
