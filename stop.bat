@echo off
title TamilEdu-SLM Shutdown
color 0C
echo ==============================================================
echo             Shutting Down TamilEdu-SLM Services
echo ==============================================================
echo.

:: 1. Terminate Port 8000 (FastAPI Retrieval)
echo stopping Retrieval Service on Port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a 2>nul
    echo ✓ Stopped PID %%a
)

:: 2. Terminate Port 8001 (FastAPI Generation)
echo stopping Generation Service on Port 8001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do (
    taskkill /f /pid %%a 2>nul
    echo ✓ Stopped PID %%a
)

:: 3. Terminate Port 5000 (Node.js Gateway)
echo stopping Express Gateway on Port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a 2>nul
    echo ✓ Stopped PID %%a
)

:: 4. Terminate Port 3000 (React Frontend)
echo stopping React Frontend on Port 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a 2>nul
    echo ✓ Stopped PID %%a
)

:: 5. Stop Redis container
echo stopping Redis container...
docker stop tamiledu-redis >nul 2>&1
if %errorlevel% EQU 0 (
    echo ✓ Stopped Docker Redis container.
)

echo.
echo ==============================================================
echo ✓ All TamilEdu-SLM stack services terminated successfully.
echo ==============================================================
echo.
pause
