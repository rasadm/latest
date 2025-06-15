@echo off
echo Starting AgenticAI Content Management Dashboard...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import tkinter, requests, schedule" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install requests schedule
)

REM Launch the dashboard
echo Launching Content Management Dashboard...
python content_dashboard.py

pause 