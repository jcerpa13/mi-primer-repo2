@echo off
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] No se encontro el comando "python".
    echo Instala Python desde https://www.python.org/downloads/
    echo y marca la casilla "Add python.exe to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] No se pudo crear el entorno virtual. Revisa el mensaje de arriba.
        echo.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat

echo Instalando dependencias (puede tardar un par de minutos la primera vez)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Fallo la instalacion de dependencias. Revisa el mensaje de arriba.
    echo.
    pause
    exit /b 1
)

echo.
echo Servidor iniciando... Desde el celular (misma red WiFi) entra a la IP de este PC, puerto 8000
echo Ejemplo: http://192.168.1.XX:8000
echo (Puedes ver tu IP local con el comando: ipconfig)
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000

echo.
echo El servidor se detuvo o fallo al iniciar. Revisa el mensaje de arriba.
pause
