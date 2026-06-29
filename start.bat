@echo off
title TamilEdu-SLM Launcher
color 0B
echo ==============================================================
echo             TamilEdu-SLM Bilingual RAG Stack
echo ==============================================================
echo.

:: 1. Diagnostic Checks
echo [1/5] Running Ingestion/OCR Diagnostic Check...
.\.venv\Scripts\python.exe -c "import sys; sys.path.append('backend/retrieval-service'); from app.ingestion.hardware_detector import log_ocr_status; log_ocr_status()"
echo.

:: 2. Check Ollama Service
echo [2/5] Checking Ollama Service status...
netstat -ano | findstr 11434 >nul
if %errorlevel% neq 0 (
    echo ⚠️ WARNING: Ollama is not running on port 11434!
    echo    Please start Ollama Desktop on your Windows machine.
    echo.
) else (
    echo ✓ Ollama is running.
)

:: 3. Start Redis
echo [3/5] Starting Redis Cache container...
docker start tamiledu-redis 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Redis Docker container not found or failed to start.
    echo    Falling back to in-memory dictionary caching for session memory.
    echo.
) else (
    echo ✓ Redis container started.
)

:: 4. Start Backend Microservices
echo [4/5] Starting Python FastAPI Microservices...

echo -- Starting Retrieval Service on http://127.0.0.1:8000...
start "TamilEdu-SLM: Retrieval Service [8000]" /D "backend\retrieval-service" cmd /c "..\..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000"

echo -- Starting Generation Service on http://127.0.0.1:8001...
start "TamilEdu-SLM: Generation Service [8001]" /D "backend\generation-service" cmd /c "..\..\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8001"

echo -- Starting Node.js Express Gateway on http://127.0.0.1:5000...
start "TamilEdu-SLM: Express Gateway [5000]" /D "backend\gateway" cmd /c "npm start"
echo.

:: 5. Start React Frontend
echo [5/5] Starting React Frontend Client on http://localhost:3000...
start "TamilEdu-SLM: React Frontend [3000]" /D "frontend" cmd /c "npm start"
echo.

echo ==============================================================
echo ✓ All services started in background terminal sessions.
echo.
echo - Retrieval API:    http://127.0.0.1:8000
echo - Generation API:   http://127.0.0.1:8001
echo - Node Gateway:     http://127.0.0.1:5000
echo - React Frontend:   http://localhost:3000
echo.
echo To shut down all services safely, double-click: stop.bat
echo ==============================================================
echo.
pause
