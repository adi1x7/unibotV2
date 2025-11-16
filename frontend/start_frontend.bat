@echo off
echo Starting UniBot Frontend...
echo.
echo Step 1: Starting API Server...
start "UniBot API Server" cmd /k "cd /d %~dp0.. && python frontend\api_server.py"
ping 127.0.0.1 -n 4 >nul
echo.
echo Step 2: Starting Frontend Server...
start "UniBot Frontend" cmd /k "cd /d %~dp0 && python -m http.server 8080"
ping 127.0.0.1 -n 3 >nul
echo.
echo ========================================
echo Frontend is starting!
echo.
echo API Server: http://127.0.0.1:8000
echo Frontend: http://localhost:8080
echo.
echo Open http://localhost:8080 in your browser
echo.
echo Press any key to close this window (servers will keep running)
echo ========================================
pause >nul

