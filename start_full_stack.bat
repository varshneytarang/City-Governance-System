@echo off
echo ========================================
echo Starting City Governance Full Stack
echo ========================================
echo.
echo This will start:
echo   1. Backend API (Port 8000)
echo   2. Frontend Dev Server (Port 5173)
echo.
echo Press Ctrl+C in each window to stop
echo ========================================
echo.

echo Starting Backend...
start "Backend API" cmd /k "python start_backend.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "Frontend Dev" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Services Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Test Page: http://localhost:5173/#test
echo API Docs: http://localhost:8000/docs
echo.
echo ========================================
