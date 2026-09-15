@echo off
echo ============================================================
echo   MMDB App Runner
echo ============================================================

if not exist .venv goto no_venv

echo Starting FastAPI Backend in a new window...
start "MMDB Backend (FastAPI)" cmd /k ".venv\Scripts\activate.bat && uvicorn src.main:app --reload --host 127.0.0.1 --port 8000"

echo Starting Streamlit Dashboard in a new window...
start "MMDB Dashboard (Streamlit)" cmd /k ".venv\Scripts\activate.bat && streamlit run src/ui/streamlit_app.py"

echo Both services have been started!
echo - FastAPI docs: http://127.0.0.1:8000/docs
echo - Streamlit Dashboard: http://localhost:8501
echo ============================================================
pause
exit /b 0

:no_venv
echo [ERROR] Virtual environment (.venv) not found. Please run setup.bat first.
pause
exit /b 1
