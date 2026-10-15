@echo off
title SecureFlowAI - Test Suite Runner
cd /d "%~dp0\.."
echo ================================================================================
echo  Running SecureFlowAI Automated Test Suites (Pytest)
echo ================================================================================
echo.
.\.venv\Scripts\pytest.exe -v
pause
