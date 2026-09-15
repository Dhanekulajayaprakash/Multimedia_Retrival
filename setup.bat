@echo off
echo ============================================================
echo   MMDB Project Setup Tool
echo ============================================================

:: Check Python 3.11 installation
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.11 was not found on your system.
    echo Please make sure Python 3.11 is installed.
    pause
    exit /b %errorlevel%
)

echo [1/4] Creating virtual environment (.venv)...
py -3.11 -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b %errorlevel%
)

echo [2/4] Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade pip.
    pause
    exit /b %errorlevel%
)

echo [3/4] Installing requirements (this might take a few minutes)...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b %errorlevel%
)

echo [4/4] Downloading spaCy model...
.venv\Scripts\python.exe -m spacy download en_core_web_sm
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download spaCy model.
    pause
    exit /b %errorlevel%
)

echo ============================================================
echo   Setup completed successfully!
echo   To run the diagnostics, run: .venv\Scripts\python.exe run_diagnostic.py
echo ============================================================
pause
