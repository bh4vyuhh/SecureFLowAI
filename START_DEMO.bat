@echo off
title SecureFlow AI - Enterprise Banking DLP Platform [LIVE DEMO LAUNCHER]
color 0A
cd /d "%~dp0"

echo ================================================================================
echo          SECUREFLOW AI - ENTERPRISE BANKING DLP PLATFORM
echo                     LIVE DEMONSTRATION SUITE
echo ================================================================================
echo.

:: 1. Verify Virtual Environment
if not exist ".\.venv\Scripts\python.exe" (
    color 0C
    echo [ERROR] Python virtual environment not found in .\.venv\
    echo Please ensure the project virtual environment is installed.
    pause
    exit /b 1
)

:: 2. Check Node & Admin Dependencies
if not exist "admin\node_modules" (
    echo [INFO] Installing admin portal dependencies...
    call npm --prefix admin install
)

echo [1/3] Terminating any stale dev processes on ports 8000 and 5174...
powershell -Command "Get-NetTCPConnection -LocalPort 8000,5174 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
timeout /t 1 /nobreak >nul

echo [2/3] Launching AI Microservice (FastAPI + ONNX INT8 Engine on Port 8000)...
start "SecureFlow AI - AI Microservice (Port 8000)" cmd /k "title AI Microservice (Port 8000) && .\.venv\Scripts\uvicorn.exe app.main:app --app-dir ai-service --host 127.0.0.1 --port 8000"

:: Wait for FastAPI to bind
echo Waiting for AI engine initialization...
:WAIT_API
timeout /t 2 /nobreak >nul
powershell -Command "try { $r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 2; if ($r.status -eq 'HEALTHY') { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo ...warming up INT8 model session...
    goto WAIT_API
)
echo [OK] AI Microservice is HEALTHY.

echo [3/3] Launching Admin SOC Console (Vite on Port 5174)...
start "SecureFlow AI - Admin SOC Console (Port 5174)" cmd /k "title Admin SOC Portal (Port 5174) && npm --prefix admin run dev"

timeout /t 3 /nobreak >nul

echo.
echo ================================================================================
echo [SUCCESS] ALL SECUREFLOW AI SERVICES ARE OPERATIONAL!
echo ================================================================================
echo   - Backend Microservice:  http://127.0.0.1:8000
echo   - Microservice Health:   http://127.0.0.1:8000/health
echo   - Live Threat Bus (WS):  ws://127.0.0.1:8000/ws/live-threats
echo   - Admin SOC Console:     http://localhost:5174/?demo=1
echo ================================================================================
echo.

echo Launching browser to Admin SOC Console...
start http://localhost:5174/?demo=1

:MENU
echo.
echo --------------------------------------------------------------------------------
echo                         LIVE DEMO CONTROL PANEL
echo --------------------------------------------------------------------------------
echo   [1] Trigger Real-Time Client Traffic Simulator (Push 30 Events to Dashboard)
echo   [2] View Ready-to-Copy Test Payloads (data\demo_samples\DEMO_PAYLOADS.txt)
echo   [3] Open Sample Banking Files Folder for File Scanner Drag-and-Drop
echo   [4] Run Full System Verification Tests (Pytest)
echo   [5] Launch Legacy Reference Frontend (Port 5173)
echo   [Q] Quit and Stop All Demo Services
echo --------------------------------------------------------------------------------
set /p choice="Select an action [1-5, Q]: "

if /i "%choice%"=="1" (
    echo.
    echo Running background client traffic simulator...
    .\.venv\Scripts\python.exe scripts\simulate_client_traffic.py
    echo [DONE] Traffic simulation complete. Check browser for live notifications!
    goto MENU
)

if /i "%choice%"=="2" (
    notepad data\demo_samples\DEMO_PAYLOADS.txt
    goto MENU
)

if /i "%choice%"=="3" (
    explorer data\demo_samples
    goto MENU
)

if /i "%choice%"=="4" (
    echo Running Pytest suite...
    .\.venv\Scripts\pytest.exe ai-service\tests
    goto MENU
)

if /i "%choice%"=="5" (
    start "SecureFlow AI - Legacy Frontend (Port 5173)" cmd /k "title Legacy Frontend (Port 5173) && npm --prefix frontend run dev"
    timeout /t 2 /nobreak >nul
    start http://localhost:5173/
    goto MENU
)

if /i "%choice%"=="Q" (
    echo.
    echo Shutting down demo services...
    powershell -Command "Get-NetTCPConnection -LocalPort 8000,5174,5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
    echo All demo services terminated.
    pause
    exit /b 0
)

echo Invalid selection. Please choose 1, 2, 3, 4, 5, or Q.
goto MENU
