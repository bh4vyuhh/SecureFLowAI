@echo off
title SecureFlowAI - Corporate Banking Admin Console (Port 5174)
cd /d "%~dp0\..\admin"
echo ================================================================================
echo  Starting New Corporate Banking Admin Console on http://localhost:5174
echo ================================================================================
echo.
npm run dev
pause
