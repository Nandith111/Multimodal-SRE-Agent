@echo off
echo =========================================
echo       Starting SRE Agent Services
echo =========================================

echo [1/3] Starting FastAPI Backend...
start "SRE Agent API" cmd /k "uvicorn api.main:app --reload"

echo [2/3] Starting Celery Worker...
start "SRE Celery Worker" cmd /k "celery -A worker.celery_app worker --loglevel=info --pool=threads"

echo [3/3] Starting Streamlit Dashboard...
start "SRE Dashboard" cmd /k "streamlit run dashboard\app.py"

echo.
echo All services are spinning up in separate windows!
echo You can now use the Streamlit Dashboard to tail your logs.
