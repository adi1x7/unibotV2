#!/bin/bash

echo "========================================"
echo "Starting UniBot Frontend..."
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python is not installed or not in PATH"
    exit 1
fi

# Verify setup
echo "[INFO] Verifying setup..."
cd "$PARENT_DIR"
python3 frontend/verify_setup.py 2>/dev/null || python frontend/verify_setup.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Setup verification failed. Please fix the issues above."
    exit 1
fi
echo ""

echo "[Step 1/2] Starting API Server..."
cd "$PARENT_DIR"
python3 frontend/api_server.py 2>/dev/null || python frontend/api_server.py &
API_PID=$!
sleep 5

echo ""
echo "Step 2: Starting Frontend Server..."
cd frontend
python -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Frontend is starting!"
echo ""
echo "API Server: http://127.0.0.1:8001"
echo "Frontend: http://localhost:8080"
echo ""
echo "Open http://localhost:8080 in your browser"
echo "Press Ctrl+C to stop both servers"
echo "========================================"

# Wait for user interrupt
trap "kill $API_PID $FRONTEND_PID; exit" INT TERM
wait

