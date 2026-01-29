@echo off
title MindWorx SOR Web Dashboard
echo ============================================================
echo MindWorx SOR Automation - Web Dashboard
echo ============================================================
echo.

:: Check if we need to install dependencies
if not exist "web\node_modules" (
    echo Installing web dependencies...
    cd web
    call npm install
    cd ..
)

:: Start Flask API in background
echo Starting Flask API on http://localhost:5000...
start /min cmd /c "python api\app.py"

:: Wait a moment for API to start
timeout /t 3 /nobreak >nul

:: Start Next.js frontend
echo Starting Next.js frontend on http://localhost:3000...
cd web
call npm run dev
