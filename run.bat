@echo off
title NOVA-X AI Homework Assistant
echo.
echo    ========================================
echo    NOVA-X: Next-Gen Omniscient VAssistant X
echo    ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check if dependencies are installed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM Install dependencies
pip install -q -r requirements.txt

REM Launch NOVA-X
python nova_x.py %*

pause
