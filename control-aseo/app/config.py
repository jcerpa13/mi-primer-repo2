"""Configuración del sistema de control de aseo.

Edita CHECKLISTS para agregar/quitar áreas o ítems a fotografiar.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
DB_PATH = DATA_DIR / "control_aseo.db"

DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# Checklist de fotos requeridas por tipo de área.
CHECKLISTS = {
    "Habitación": ["Cama", "Piso", "Velador/Superficies", "Basurero", "Ventana"],
    "Baño": ["WC", "Ducha", "Lavamanos", "Espejo", "Piso"],
    "Cocina": ["Mesón", "Lavaplatos", "Piso", "Basurero", "Estufa"],
    "Área común": ["Piso", "Superficies", "Basurero", "Orden general"],
}

NIVELES = ["Alto", "Medio", "Bajo"]

# Orden de severidad para calcular el resultado general (el peor ítem manda).
ORDEN_SEVERIDAD = {"Bajo": 0, "Medio": 1, "Alto": 2}

# --- Configuración de IA local ---
# Si Ollama está instalado y corriendo en el mismo PC (https://ollama.com),
# se usará un modelo de visión para un análisis más inteligente.
# Si no está disponible, se usa automáticamente un analizador heurístico
# (OpenCV) que funciona sin instalar nada extra.
OLLAMA_URL = "http://localhost:11434"
OLLAMA_VISION_MODEL = "llava"  # también sirve "moondream", "bakllava", etc.
OLLAMA_TIMEOUT_SEGUNDOS = 25
