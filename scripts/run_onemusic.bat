@echo off
setlocal

cd /d %~dp0

start "OneMusic API" cmd /k "cd backend && .venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
start "OneMusic Frontend" cmd /k "cd frontend-dist && npx --yes serve -l 5173 ."

echo OneMusic AI is starting...
echo API: http://127.0.0.1:8000
echo UI:  http://127.0.0.1:5173
