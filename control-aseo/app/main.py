import shutil
import socket
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import database
from .ai_analysis import analizar_imagen
from .config import BASE_DIR, CHECKLISTS, ORDEN_SEVERIDAD, UPLOADS_DIR

app = FastAPI(title="Control de Aseo")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/fotos", StaticFiles(directory=UPLOADS_DIR), name="fotos")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def _startup():
    database.init_db()


def _ip_local() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"areas": list(CHECKLISTS.keys()), "ip_local": _ip_local()},
    )


@app.post("/iniciar")
def iniciar(encargado: str = Form(...), area: str = Form(...)):
    encargado = encargado.strip()
    if not encargado:
        raise HTTPException(400, "El nombre del encargado es obligatorio.")
    if area not in CHECKLISTS:
        raise HTTPException(400, "Área inválida.")

    sesion_id = database.crear_sesion(encargado, area, CHECKLISTS[area])
    return RedirectResponse(f"/aseo/{sesion_id}", status_code=303)


@app.get("/aseo/{sesion_id}")
def ver_aseo(request: Request, sesion_id: int):
    sesion, items = database.obtener_sesion(sesion_id)
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada.")
    return templates.TemplateResponse(
        request, "aseo.html", {"sesion": sesion, "items": items}
    )


@app.post("/aseo/{sesion_id}/foto/{nombre_item}")
async def subir_foto(sesion_id: int, nombre_item: str, foto: UploadFile):
    sesion, items = database.obtener_sesion(sesion_id)
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada.")
    if sesion["estado"] != "en_progreso":
        raise HTTPException(400, "Esta sesión ya fue finalizada.")
    nombres_validos = {i["nombre_item"] for i in items}
    if nombre_item not in nombres_validos:
        raise HTTPException(400, "Ítem no pertenece a esta sesión.")

    carpeta_sesion = UPLOADS_DIR / str(sesion_id)
    carpeta_sesion.mkdir(exist_ok=True)
    extension = Path(foto.filename or "foto.jpg").suffix or ".jpg"
    nombre_archivo = f"{nombre_item.replace('/', '-')}{extension}"
    ruta_destino = carpeta_sesion / nombre_archivo

    with ruta_destino.open("wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    nivel, retro, motor = analizar_imagen(str(ruta_destino), nombre_item)

    ruta_relativa = f"{sesion_id}/{nombre_archivo}"
    database.guardar_resultado_item(sesion_id, nombre_item, ruta_relativa, nivel, retro, motor)

    return {
        "item": nombre_item,
        "nivel": nivel,
        "retroalimentacion": retro,
        "motor_ia": motor,
        "foto_url": f"/fotos/{ruta_relativa}",
    }


@app.post("/aseo/{sesion_id}/finalizar")
def finalizar(sesion_id: int):
    sesion, items = database.obtener_sesion(sesion_id)
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada.")

    niveles_evaluados = [i["nivel"] for i in items if i["nivel"]]
    if not niveles_evaluados:
        raise HTTPException(400, "Aún no se ha subido ninguna foto.")

    nivel_general = max(niveles_evaluados, key=lambda n: ORDEN_SEVERIDAD[n])
    database.finalizar_sesion(sesion_id, nivel_general)
    return RedirectResponse(f"/aseo/{sesion_id}", status_code=303)


@app.get("/historial")
def historial(request: Request):
    sesiones = database.listar_sesiones()
    return templates.TemplateResponse(request, "historial.html", {"sesiones": sesiones})


@app.get("/historial/{sesion_id}")
def detalle_sesion(request: Request, sesion_id: int):
    sesion, items = database.obtener_sesion(sesion_id)
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada.")
    return templates.TemplateResponse(
        request, "detalle.html", {"sesion": sesion, "items": items}
    )
