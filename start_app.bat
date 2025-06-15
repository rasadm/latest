@echo off
echo ==========================================
echo Starting AI Content Management System
echo ==========================================

REM Set the Python path to include the current directory
set PYTHONPATH=%~dp0

REM Load environment variables from .env file if it exists
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do set %%a=%%b
)

REM Start the main project dashboard
echo Starting Project Dashboard...
python dashboards/project_dashboard.py

pause 