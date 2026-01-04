@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Starting UniBot Frontend...
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PARENT_DIR=%SCRIPT_DIR%..

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Verify setup
echo [INFO] Verifying setup...
cd /d "%PARENT_DIR%"
python frontend\verify_setup.py
if errorlevel 1 (
    echo.
    echo [ERROR] Setup verification failed. Please fix the issues above.
    pause
    exit /b 1
)
echo.

echo [Step 1/2] Starting API Server...
cd /d "%PARENT_DIR%"
start "UniBot API Server" cmd /k "python frontend\api_server.py"
if errorlevel 1 (
    echo [ERROR] Failed to start API server
    pause
    exit /b 1
)

REM Wait for API server to start
echo Waiting for API server to initialize...
timeout /t 5 /nobreak >nul

REM Check if API server is responding
echo Checking API server status...
for /l %%i in (1,1,10) do (
    curl -s http://127.0.0.1:8001/health >nul 2>&1
    if not errorlevel 1 (
        echo [OK] API server is responding
        goto :server_ready
    )
    timeout /t 1 /nobreak >nul
)
echo [WARNING] API server may not be ready yet, but continuing...

:server_ready
echo.
echo [Step 2/2] Starting Frontend Server...
cd /d "%SCRIPT_DIR%"
start "UniBot Frontend" cmd /k "python -m http.server 8080"
if errorlevel 1 (
    echo [ERROR] Failed to start frontend server
    pause
    exit /b 1
)

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Frontend is starting!
echo ========================================
echo.
echo API Server: http://127.0.0.1:8001
echo Frontend:   http://localhost:8080
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:8080
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
echo Press any key to close this window...
echo ========================================
pause >nul

