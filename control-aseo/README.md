# Control de Aseo (servidor local + IA local)

Aplicación que corre **en tu PC** como servidor local. Te conectas desde el
celular por la misma red WiFi, registras el inicio del aseo, subes una foto
por cada ítem solicitado (WC, ducha, cama, etc.) y cada foto se analiza al
instante con **IA local** (nada se sube a internet) para asignar un
estándar **Alto / Medio / Bajo** y dar retroalimentación a quien hizo el aseo.

## Requisitos

- Python 3.10 o superior instalado en el PC.
- El PC y el celular conectados a **la misma red WiFi**.

## Cómo correrlo

### Windows
Doble clic en `run.bat` (o desde CMD: `run.bat`).

### Mac / Linux
```bash
chmod +x run.sh
./run.sh
```

El script instala automáticamente las dependencias en un entorno virtual
(`.venv`) la primera vez, y luego muestra algo como:

```
Desde el celular (misma red WiFi) entra a:
  http://192.168.1.25:8000
```

Abre esa dirección en el navegador del celular (Chrome/Safari, no requiere
instalar ninguna app). Puedes incluso guardarla como acceso directo en la
pantalla de inicio del celular.

Si el script no muestra la IP, en el PC ejecuta:
- Windows: `ipconfig` (busca "Dirección IPv4")
- Mac/Linux: `hostname -I` o `ifconfig`

## Cómo se usa

1. En el celular, abre la página principal, escribe el nombre del encargado
   y elige el área (Habitación, Baño, Cocina, Área común). Al presionar
   **"Iniciar aseo"** queda registrada la hora de inicio.
2. Aparece la lista de ítems a fotografiar según el área (por ejemplo, para
   "Baño": WC, Ducha, Lavamanos, Espejo, Piso).
3. Para cada ítem, toca "Tomar / subir foto" → se abre la cámara del
   celular → la foto se envía al PC y se analiza automáticamente.
4. Al instante aparece el resultado (Alto/Medio/Bajo) y una recomendación de
   qué mejorar si corresponde. Se puede repetir la foto las veces que sea
   necesario.
5. Al terminar todos los ítems, presiona **"Finalizar aseo"**: se registra
   la hora de término y el resultado general (el peor nivel obtenido entre
   todos los ítems).
6. Cualquier persona en la red (por ejemplo el supervisor, desde el mismo
   PC o desde otro celular) puede entrar a `/historial` para ver todos los
   aseos registrados, con fotos y retroalimentación.

## Sobre el análisis con IA local

Por defecto la app funciona sin instalar nada adicional, usando un
analizador basado en visión por computador (OpenCV): mide nitidez,
iluminación y "densidad de desorden" visual (bordes y variación de color)
para estimar el nivel. Es un punto de partida razonable, pero es una
heurística simple, no un modelo entrenado en fotos de aseo reales.

### Análisis más inteligente (opcional, recomendado): Ollama + modelo de visión

Si quieres que la IA "entienda" mejor la foto (por ejemplo, distinguir una
cama bien tendida de una desordenada con mucho más criterio), instala
[Ollama](https://ollama.com) en el mismo PC —funciona 100% local, sin
internet una vez descargado el modelo— y baja un modelo de visión:

```bash
ollama pull llava
```

Con Ollama corriendo en el PC (queda escuchando en `localhost:11434`), la
aplicación lo detecta automáticamente y lo usa para analizar cada foto y
generar la retroalimentación. Si Ollama no está disponible, la app sigue
funcionando con el analizador heurístico, sin que tengas que configurar
nada.

Puedes cambiar el modelo usado editando `OLLAMA_VISION_MODEL` en
`app/config.py` (por ejemplo `moondream` es más liviano para PCs modestos).

## Personalizar las áreas e ítems a fotografiar

Edita el diccionario `CHECKLISTS` en `app/config.py` para agregar,
quitar o renombrar áreas e ítems según tus necesidades.

## Estructura del proyecto

```
control-aseo/
  app/
    main.py          # servidor FastAPI y rutas
    ai_analysis.py    # análisis de imágenes (Ollama + heurística OpenCV)
    database.py        # acceso a SQLite
    config.py           # checklist de áreas/ítems y configuración de IA
  templates/            # páginas HTML (Jinja2)
  static/                # CSS y JS del frontend
  data/                    # base de datos SQLite (se crea sola)
  uploads/                  # fotos subidas, organizadas por sesión
  run.sh / run.bat            # scripts de arranque
```

Los datos (`data/`) y las fotos (`uploads/`) quedan solo en tu PC.
