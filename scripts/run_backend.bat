@echo off
cd /d "%~dp0..\apps\backend"
python -m uvicorn app.main:app --reload --port 8000
