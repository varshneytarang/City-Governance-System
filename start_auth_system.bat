@echo off
REM Quick Start Script for City Governance Authentication System
REM This script sets up and starts the authentication system

echo ========================================
echo City Governance AI - Auth Quick Start
echo ========================================
echo.

REM Step 1: Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please create virtual environment first:
    echo   python -m venv .venv
    pause
    exit /b 1
)

REM Step 2: Activate virtual environment
echo [1/6] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Step 3: Install dependencies
echo.
echo [2/6] Installing authentication dependencies...
pip install -q bcrypt PyJWT google-auth google-auth-oauthlib google-auth-httplib2
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!

REM Step 4: Check database connection
echo.
echo [3/6] Checking database connection...
python -c "import psycopg2; conn = psycopg2.connect('host=localhost port=5432 dbname=city_mas user=postgres password=passwordpassword'); print('Database connected!'); conn.close()" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Could not connect to database!
    echo Please ensure PostgreSQL is running and city_mas database exists.
    echo.
    echo To fix:
    echo   1. Start PostgreSQL
    echo   2. Create database: createdb -U postgres city_mas
    echo   3. Run migration: psql -U postgres -d city_mas -f backend\migrations\auth_schema.sql
    echo.
    pause
)

REM Step 5: Check if migration is needed
echo.
echo [4/6] Checking if database migration is needed...
python -c "import psycopg2; conn = psycopg2.connect('host=localhost port=5432 dbname=city_mas user=postgres password=passwordpassword'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_name=''users'''); exists = cur.fetchone()[0] > 0; conn.close(); exit(0 if exists else 1)" 2>nul
if %errorlevel% neq 0 (
    echo Migration needed!
    echo.
    echo Would you like to run the database migration now? (Y/N)
    set /p confirm=
    if /i "%confirm%"=="Y" (
        echo Running migration...
        psql -U postgres -d city_mas -f backend\migrations\auth_schema.sql
        if %errorlevel% neq 0 (
            echo ERROR: Migration failed!
            pause
            exit /b 1
        )
        echo Migration completed successfully!
    ) else (
        echo Skipping migration. Please run manually:
        echo   psql -U postgres -d city_mas -f backend\migrations\auth_schema.sql
    )
) else (
    echo Database tables already exist.
)

REM Step 6: Display instructions
echo.
echo [5/6] Setup complete!
echo.
echo ========================================
echo   Next Steps:
echo ========================================
echo.
echo 1. Start Backend (Terminal 1):
echo    python -m uvicorn backend.app.server:app --reload --port 8000
echo.
echo 2. Start Frontend (Terminal 2):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Test Authentication:
echo    python test_auth_system.py
echo.
echo 4. Open Browser:
echo    Login:    http://localhost:5173/login.html
echo    Register: http://localhost:5173/register.html
echo.
echo 5. Test Accounts:
echo    Admin:    admin@citygovernance.in / admin123
echo    Fire:     fire.dept@citygovernance.in / admin123
echo    Water:    water.dept@citygovernance.in / admin123
echo.
echo ========================================
echo.

REM Step 7: Ask if user wants to start backend now
echo [6/6] Would you like to start the backend server now? (Y/N)
set /p start=
if /i "%start%"=="Y" (
    echo.
    echo Starting backend server...
    echo Press Ctrl+C to stop the server
    echo.
    python -m uvicorn backend.app.server:app --reload --port 8000
) else (
    echo.
    echo To start manually, run:
    echo   python -m uvicorn backend.app.server:app --reload --port 8000
    echo.
    pause
)
