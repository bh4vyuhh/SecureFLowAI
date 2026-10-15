@echo off
title SecureFlowAI - AI Microservice (FastAPI + ONNX INT8)
cd /d "%~dp0\.."
echo ================================================================================
echo  Starting SecureFlowAI Banking DLP Microservice on http://localhost:8000
echo ================================================================================
echo.
.\.venv\Scripts\uvicorn.exe app.main:app --app-dir ai-service --host 0.0.0.0 --port 8000 --reload
pause
