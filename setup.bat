@echo off
REM NutriLens AI - Automated Setup Script for Windows
REM This script sets up the entire application for local development

echo ==========================================
echo NutriLens AI - Automated Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed
    echo Please install Node.js 18 or higher
    pause
    exit /b 1
)

echo [OK] Node.js found
node --version
echo.

REM Backend Setup
echo ==========================================
echo Setting up Backend...
echo ==========================================
cd backend

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo [WARNING] Please update DATABASE_URL in backend\.env
)

echo [OK] Backend setup complete
cd ..
echo.

REM Frontend Setup
echo ==========================================
echo Setting up Frontend...
echo ==========================================
cd frontend

REM Install dependencies
echo Installing Node.js dependencies...
call npm install

REM Create .env.local file if it doesn't exist
if not exist .env.local (
    echo Creating .env.local file...
    copy .env.example .env.local
)

echo [OK] Frontend setup complete
cd ..
echo.

REM Summary
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo.
echo 1. Configure Database:
echo    - Update DATABASE_URL in backend\.env
echo    - Create PostgreSQL database
echo.
echo 2. Start Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python main.py
echo.
echo 3. Start Frontend (in new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 4. Visit http://localhost:3000
echo.
echo Happy coding! 🚀
echo.
pause
