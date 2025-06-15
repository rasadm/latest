@echo off
echo ==========================================
echo Starting AI Content Management System
echo ==========================================

REM Set the Python path to include the current directory
set PYTHONPATH=%~dp0

REM Start the main project dashboard
echo Starting Project Dashboard...
python dashboards/project_dashboard.py

pause 