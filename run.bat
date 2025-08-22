@echo off
title BNS Legal Assistant

echo.
echo ================================================================
echo    BNS Legal Assistant - Starting Application
echo    AI-Powered Legal Consultation System  
echo ================================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run install.bat first to set up the application.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo ================================================================
    echo    CONFIGURATION REQUIRED
    echo ================================================================
    echo.
    echo Error: .env configuration file not found!
    echo.
    echo Please follow these steps:
    echo 1. Copy .env.example to .env
    echo 2. Edit .env and add your OpenAI API key
    echo 3. Run this script again
    echo.
    echo Get your OpenAI API key from: https://platform.openai.com/
    echo.
    pause
    exit /b 1
)

REM Check if data directory has PDF files
echo Checking for BNS PDF documents...
set pdf_found=0
for %%f in (data\*.pdf) do set pdf_found=1

if %pdf_found%==0 (
    echo.
    echo ================================================================
    echo    PDF DOCUMENTS NEEDED
    echo ================================================================
    echo.
    echo Warning: No PDF files found in the data directory!
    echo.
    echo Please place BNS PDF documents in the 'data' folder.
    echo The system will work but won't have legal content to reference.
    echo.
    echo Continue anyway? (y/n)
    set /p continue=
    if /i not "%continue%"=="y" (
        echo Setup cancelled.
        pause
        exit /b 1
    )
)

echo.
echo Starting BNS Legal Assistant...
echo.
echo ================================================================
echo    Server will start at: http://localhost:5000
echo    Press Ctrl+C to stop the server
echo ================================================================
echo.

REM Start the Flask application
python app.py

echo.
echo Application stopped.
pause