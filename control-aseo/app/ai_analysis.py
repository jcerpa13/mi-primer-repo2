"""Análisis de fotos con IA local.

Estrategia híbrida, 100% local (ninguna imagen sale del PC):

1. Si hay un servidor Ollama corriendo en el mismo equipo con un modelo de
   visión (ej. `ollama run llava`), se le pide que evalúe la foto y entregue
   nivel + retroalimentación. Esto da el análisis más "inteligente".
2. Si Ollama no está disponible, se usa un analizador heurístico con OpenCV
   (nitidez, iluminación y densidad de "desorden" visual) que funciona sin
   instalar nada adicional. Es más simple, pero deja el sistema 100%
   funcional desde el primer momento.
"""
import base64
import json
import re

import cv2
import numpy as np
import requests

from .config import OLLAMA_URL, OLLAMA_VISION_MODEL, OLLAMA_TIMEOUT_SEGUNDOS

FEEDBACK_HEURISTICO = {
    "Alto": "Se ve ordenado y limpio. ¡Buen trabajo!",
    "Medio": "Aceptable, pero se notan detalles por mejorar (revisa orden y manchas visibles).",
    "Bajo": "No cumple el estándar esperado. Vuelve a repasar esta zona antes de continuar.",
}


def _ollama_disponible() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=1.5)
        return r.status_code == 200
    except requests.RequestException:
        return False


def _analizar_con_ollama(ruta_imagen: str, nombre_item: str):
    with open(ruta_imagen, "rb") as f:
        imagen_b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = (
        f"Eres un supervisor de aseo/housekeeping. Te muestro una foto de: '{nombre_item}'. "
        "Evalúa qué tan limpio y ordenado está, según estándares de un hotel/residencia. "
        "Responde SOLO un JSON válido, sin texto adicional, con este formato exacto: "
        '{"nivel": "Alto" | "Medio" | "Bajo", "retroalimentacion": "una frase corta en español '
        'explicando el motivo y qué mejorar si aplica"}. '
        "Alto = impecable, Medio = aceptable con detalles menores, Bajo = no cumple el estándar."
    )

    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_VISION_MODEL,
            "prompt": prompt,
            "images": [imagen_b64],
            "stream": False,
        },
        timeout=OLLAMA_TIMEOUT_SEGUNDOS,
    )
    resp.raise_for_status()
    texto = resp.json().get("response", "")

    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if not match:
        raise ValueError(f"Respuesta de Ollama sin JSON reconocible: {texto!r}")

    datos = json.loads(match.group(0))
    nivel = str(datos.get("nivel", "")).strip().capitalize()
    if nivel not in ("Alto", "Medio", "Bajo"):
        raise ValueError(f"Nivel inválido devuelto por Ollama: {nivel!r}")

    retro = str(datos.get("retroalimentacion", "")).strip() or FEEDBACK_HEURISTICO[nivel]
    return nivel, retro


def _analizar_heuristico(ruta_imagen: str, nombre_item: str):
    img = cv2.imread(ruta_imagen)
    if img is None:
        return "Medio", "No se pudo leer la imagen correctamente; se asignó un nivel neutro."

    img = cv2.resize(img, (600, 600), interpolation=cv2.INTER_AREA)
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Nitidez: fotos muy borrosas no permiten evaluar bien.
    nitidez = cv2.Laplacian(gris, cv2.CV_64F).var()
    if nitidez < 15:
        return "Medio", "La foto salió borrosa; intenta tomarla de nuevo con más luz y firmeza."

    # Iluminación promedio.
    brillo = float(np.mean(gris))

    # Densidad de bordes: superficies ordenadas/lisas tienden a tener menos
    # bordes que superficies con objetos sueltos, arrugas o manchas.
    bordes = cv2.Canny(gris, 60, 150)
    densidad_bordes = float(np.count_nonzero(bordes)) / bordes.size

    # Variación de color: más variación puede indicar manchas u objetos
    # fuera de lugar en una superficie que debería ser uniforme.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    variacion_color = float(np.std(hsv[:, :, 1]))

    # Puntaje de "desorden" combinando ambas señales (rango aprox. 0-100).
    puntaje_desorden = min(100.0, densidad_bordes * 400 + variacion_color * 0.3)

    if brillo < 40:
        return "Medio", "La foto está muy oscura para evaluar con confianza; repite con mejor iluminación."

    if puntaje_desorden < 18:
        nivel = "Alto"
    elif puntaje_desorden < 32:
        nivel = "Medio"
    else:
        nivel = "Bajo"

    return nivel, FEEDBACK_HEURISTICO[nivel]


def analizar_imagen(ruta_imagen: str, nombre_item: str):
    """Devuelve (nivel, retroalimentacion, motor_usado)."""
    if _ollama_disponible():
        try:
            nivel, retro = _analizar_con_ollama(ruta_imagen, nombre_item)
            return nivel, retro, f"ollama:{OLLAMA_VISION_MODEL}"
        except Exception:
            # Si Ollama falla por cualquier motivo, no bloqueamos el flujo:
            # caemos de forma transparente al analizador heurístico.
            pass

    nivel, retro = _analizar_heuristico(ruta_imagen, nombre_item)
    return nivel, retro, "heuristico_opencv"
