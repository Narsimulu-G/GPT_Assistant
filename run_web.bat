@echo off
echo Starting GPT Voice Assistant Web App...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

:: Install requirements if needed (optional check)
:: pip install -r requirements.txt

:: Start the Flask server
echo Starting Backend Server...
python backend_server.py

pause
