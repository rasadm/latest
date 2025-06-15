@echo off
echo Starting Project-Based Content Management Dashboard...
echo Checking dependencies...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required modules are available
python -c "import tkinter, threading, json, datetime, pathlib, uuid, dataclasses" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install -r requirements.txt
)

echo Launching Project Management Dashboard...
python project_dashboard.py

pause 