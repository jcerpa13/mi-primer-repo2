@echo off
cd /d "%~dp0"

if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo Servidor iniciando... Desde el celular (misma red WiFi) entra a la IP de este PC, puerto 8000
echo Ejemplo: http://192.168.1.XX:8000
echo (Puedes ver tu IP local con el comando: ipconfig)
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000
