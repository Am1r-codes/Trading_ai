@echo off
echo ========================================
echo    NORO AI Trading Assistant
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please copy env.example to .env and add your API keys
    echo.
    copy env.example .env
    echo Created .env file from template
    echo Please edit .env and add your API keys before running again
    pause
    exit /b 1
)

echo.
echo Starting Trading Assistant...
echo Backend will be available at: http://localhost:5000
echo Frontend: Open frontend/index.html in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python run.py

pause 