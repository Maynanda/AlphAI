#!/bin/bash

# Exit on any error
set -e

# Get directory this script lives in
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env if it exists (makes GEMINI_API_KEY etc. available to sub-processes)
if [ -f ".env" ]; then
    echo "🔑 Loading .env..."
    export $(grep -v '^#' .env | xargs)
fi

echo ""
echo "🚀 Starting Arlo — AlphaAI..."
echo "─────────────────────────────────────────"

# 1. Start FastAPI Backend (Uvicorn) in the background
echo "▶  Backend   → http://127.0.0.1:8000"
python -m uvicorn arlo.api.main:app --host 127.0.0.1 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Ensure backend process is cleaned up on exit
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID 2>/dev/null" EXIT

# 2. Wait for backend to be ready (health check loop — up to 30 seconds)
echo -n "   Waiting for backend to be ready"
MAX_WAIT=30
ELAPSED=0
until curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; do
    sleep 1
    ELAPSED=$((ELAPSED + 1))
    echo -n "."
    if [ $ELAPSED -ge $MAX_WAIT ]; then
        echo ""
        echo "❌ Backend failed to start after ${MAX_WAIT}s. Check backend.log:"
        tail -20 backend.log
        exit 1
    fi
done
echo " ✅"

echo "▶  Frontend  → http://127.0.0.1:8501"
echo "─────────────────────────────────────────"
echo ""

# 3. Start Streamlit Frontend (foreground — blocking)
python -m streamlit run arlo/ui/app.py \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false
