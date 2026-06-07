#!/bin/bash

# ──────────────────────────────────────────────────────────────────────────────

# Arlo — AlphaAI

#

# Usage:

# ./start.sh

#

# Requirements:

# Project virtual environment must exist:

#

# python3 -m venv venv

# source venv/bin/activate

# pip install -r requirements.txt

# ──────────────────────────────────────────────────────────────────────────────

set -e

# Project root

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use project venv only

PYTHON="$SCRIPT_DIR/venv/bin/python"

if [ ! -x "$PYTHON" ]; then
echo "❌ Virtual environment not found."
echo ""
echo "Create it with:"
echo "python3 -m venv venv"
echo ""
exit 1
fi

echo ""
echo "🐍 Using project virtual environment"
echo "   $PYTHON"
echo ""
echo "   $("$PYTHON" --version)"
echo ""

# Load .env

if [ -f ".env" ]; then
echo "🔑 Loading .env..."
set -a
source .env
set +a
echo ""
fi

echo "🚀 Starting Arlo — AlphaAI..."
echo "─────────────────────────────────────────"

# Start FastAPI backend

echo "▶ Backend   → http://127.0.0.1:8000"

"$PYTHON" -m uvicorn arlo.api.main:app \
--host 127.0.0.1 \
--port 8000 \
> backend.log 2>&1 &

BACKEND_PID=$!

# Cleanup

cleanup() {
echo ""
echo "🛑 Stopping services..."


if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
    kill "$BACKEND_PID"
fi

echo "✅ Shutdown complete"


}

trap cleanup EXIT INT TERM

# Wait for backend

echo -n "   Waiting for backend"

MAX_WAIT=30
ELAPSED=0

until curl -s http://127.0.0.1:8000/health > /dev/null 2>&1
do
sleep 1
ELAPSED=$((ELAPSED + 1))


echo -n "."

if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
    echo ""
    echo ""
    echo "❌ Backend failed to start."
    echo ""
    echo "Last 30 lines of backend.log:"
    echo "────────────────────────────"

    tail -30 backend.log

    exit 1
fi


done

echo " ✅"

echo ""
echo "▶ Frontend  → http://127.0.0.1:8501"
echo "─────────────────────────────────────────"
echo ""
echo "Press Ctrl+C to stop."
echo ""

# Launch Streamlit

exec "$PYTHON" -m streamlit run arlo/ui/app.py \
--server.port 8501 \
--server.headless true \
--browser.gatherUsageStats false
