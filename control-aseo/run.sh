#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt

echo ""
echo "Servidor iniciando... Desde el celular (misma red WiFi) entra a:"
python3 - <<'EOF'
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(f"  http://{s.getsockname()[0]}:8000")
s.close()
EOF
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000
