#!/bin/bash

# ──────────────────────────────────────────────────────────────────────────────
#  Arlo — AlphaAI  |  start.sh
#  Usage:
#    ./start.sh              → auto-detect Python (conda 'arlo' env preferred)
#    PYTHON=python3 ./start.sh  → override with specific interpreter
# ──────────────────────────────────────────────────────────────────────────────

# Change to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── 1. Python resolver ────────────────────────────────────────────────────────
if [ -z "$PYTHON" ]; then
    # Try conda 'arlo' env first (recommended)
    CONDA_ARLO_PYTHON="$HOME/opt/anaconda3/envs/arlo/bin/python"
    CONDA_BASE_PYTHON="$HOME/opt/anaconda3/bin/python"

    if [ -x "$CONDA_ARLO_PYTHON" ]; then
        PYTHON="$CONDA_ARLO_PYTHON"
        echo "🐍 Using conda env: arlo  ($PYTHON)"
    elif [ -x "$CONDA_BASE_PYTHON" ]; then
        PYTHON="$CONDA_BASE_PYTHON"
        echo "🐍 Using conda: base  ($PYTHON)"
    else
        PYTHON="$(which python3)"
        echo "🐍 Using system python3  ($PYTHON)"
    fi
fi

# Verify interpreter works
if ! "$PYTHON" --version > /dev/null 2>&1; then
    echo "❌ Python not found at: $PYTHON"
    echo "   Set PYTHON env var to your interpreter path, e.g.:"
    echo "   PYTHON=/path/to/python ./start.sh"
    exit 1
fi

echo ""
echo "   Python: $("$PYTHON" --version)"
echo ""

# ── 2. Load .env ──────────────────────────────────────────────────────────────
if [ -f ".env" ]; then
    echo "🔑 Loading .env..."
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

echo ""
echo "🚀 Starting Arlo — AlphaAI..."
echo "─────────────────────────────────────────"

# ── 3. FastAPI Backend ────────────────────────────────────────────────────────
echo "▶  Backend   → http://127.0.0.1:8000"
"$PYTHON" -m uvicorn arlo.api.main:app --host 127.0.0.1 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Clean up on exit
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID 2>/dev/null" EXIT

# ── 4. Health-check loop (wait up to 30s) ────────────────────────────────────
echo -n "   Waiting for backend"
MAX_WAIT=30
ELAPSED=0
until curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; do
    sleep 1
    ELAPSED=$((ELAPSED + 1))
    echo -n "."
    if [ $ELAPSED -ge $MAX_WAIT ]; then
        echo ""
        echo "❌ Backend failed to start after ${MAX_WAIT}s. Check backend.log:"
        tail -25 backend.log
        exit 1
    fi
done
echo " ✅"

echo "▶  Frontend  → http://127.0.0.1:8501"
echo "─────────────────────────────────────────"
echo ""
echo "   Press Ctrl+C to stop."
echo ""

# ── 5. Streamlit Frontend (blocking) ─────────────────────────────────────────
"$PYTHON" -m streamlit run arlo/ui/app.py \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false
