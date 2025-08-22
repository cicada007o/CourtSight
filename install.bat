@echo off
title BNS Legal Assistant - One-Click Installer

echo.
echo ================================================================
echo    BNS Legal Assistant - One-Click Windows Installer
echo    AI-Powered Legal Consultation System
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python found! Starting installation...
echo.

REM Run the setup script
python setup.py

echo.
echo Installation completed!
echo.
pause