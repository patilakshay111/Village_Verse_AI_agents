@echo off
setlocal EnableExtensions EnableDelayedExpansion
title VillageVerse Launcher
cd /d "%~dp0"
set NO_COLOR=1

echo.
echo  ========================================
echo   VillageVerse - Starting Anandgaon
echo  ========================================
echo.

echo [1/4] Stopping old servers on port 8000...
call :KillPort 8000
call :KillPort 5173
timeout /t 2 /nobreak >nul

echo [2/4] Checking UI build...
if not exist "frontend\dist\index.html" (
    echo UI not built yet. Building once...
    call :FindNpm
    if errorlevel 1 (
        echo.
        echo ERROR: Node.js/npm not found in PATH.
        echo Install from https://nodejs.org then run this file again.
        echo.
        pause
        exit /b 1
    )
    pushd frontend
    call "%NPM_CMD%" run build
    if errorlevel 1 (
        echo ERROR: UI build failed.
        popd
        pause
        exit /b 1
    )
    popd
)

echo [3/4] Starting VillageVerse (API + UI on port 8000)...
if not exist "backend\.venv\Scripts\activate.bat" (
    echo ERROR: Backend not set up. Run:
    echo   cd backend
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

start "VillageVerse" cmd /k "cd /d "%~dp0backend" && set NO_COLOR=1 && call .venv\Scripts\activate.bat && uvicorn main:app --host 127.0.0.1 --port 8000"

echo [4/4] Waiting for server...
call :WaitForPort 8000 40
if errorlevel 1 (
    echo ERROR: Server did not start. Check the VillageVerse window.
    pause
    exit /b 1
)

start "" "http://127.0.0.1:8000"
echo.
echo  Ready! Browser: http://127.0.0.1:8000
echo  API docs:     http://127.0.0.1:8000/docs
echo.
echo  One window only - keep "VillageVerse" terminal open.
echo.
pause
exit /b 0

:FindNpm
set "NPM_CMD="
where npm.cmd >nul 2>&1 && set "NPM_CMD=npm.cmd" && exit /b 0
where npm >nul 2>&1 && set "NPM_CMD=npm" && exit /b 0
if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd" && exit /b 0
if exist "%ProgramFiles(x86)%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles(x86)%\nodejs\npm.cmd" && exit /b 0
exit /b 1

:KillPort
set "_PORT=:%~1 "
for /f "tokens=5" %%P in ('netstat -ano ^| findstr "%_PORT%" ^| findstr "LISTENING"') do taskkill /F /PID %%P >nul 2>&1
exit /b 0

:WaitForPort
set "_PORT=:%~1 "
set /a _N=0
:wait_loop
netstat -ano | findstr "%_PORT%" | findstr "LISTENING" >nul
if not errorlevel 1 exit /b 0
set /a _N+=1
if !_N! geq %2 exit /b 1
timeout /t 1 /nobreak >nul
goto wait_loop
