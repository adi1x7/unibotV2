#!/bin/bash

echo "Starting UniBot Frontend..."
echo ""
echo "Step 1: Starting API Server..."
cd "$(dirname "$0")/.."
python frontend/api_server.py &
API_PID=$!
sleep 3

echo ""
echo "Step 2: Starting Frontend Server..."
cd frontend
python -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Frontend is starting!"
echo ""
echo "API Server: http://127.0.0.1:8000"
echo "Frontend: http://localhost:8080"
echo ""
echo "Open http://localhost:8080 in your browser"
echo "Press Ctrl+C to stop both servers"
echo "========================================"

# Wait for user interrupt
trap "kill $API_PID $FRONTEND_PID; exit" INT TERM
wait

