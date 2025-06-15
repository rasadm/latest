@echo off
REM Set the Python path to include the current directory
set PYTHONPATH=%~dp0

:start
echo ==========================================
echo AI Content Management System - Quick Access
echo ==========================================
echo.
echo 1. Start Project Dashboard
echo 2. Start Content Dashboard  
echo 3. Start Settings Dashboard
echo 4. Start Publishing Scheduler
echo 5. View System Organization
echo 6. Exit
echo.
set /p choice="Select option (1-6): "

if "%choice%"=="1" (
    echo Starting Project Dashboard...
    python dashboards/project_dashboard.py
) else if "%choice%"=="2" (
    echo Starting Content Dashboard...
    python dashboards/content_dashboard.py
) else if "%choice%"=="3" (
    echo Starting Settings Dashboard...
    python dashboards/settings_dashboard.py
) else if "%choice%"=="4" (
    echo Starting Publishing Scheduler...
    python publishing/publishing_scheduler.py
) else if "%choice%"=="5" (
    echo Checking System Organization...
    python organize_system.py --check
    pause
    goto start
) else if "%choice%"=="6" (
    echo Goodbye!
    exit
) else (
    echo Invalid choice. Please try again.
    pause
    goto start
)

goto start
