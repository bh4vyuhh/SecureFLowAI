@echo off
title SecureFlowAI - Old Frontend (Port 5173)
cd /d "%~dp0\..\frontend"
echo ================================================================================
echo  Starting Original Frontend on http://localhost:5173
echo ================================================================================
echo.
npm run dev
pause
