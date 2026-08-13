@echo off
setlocal EnableExtensions
title VillageVerse - Stop
cd /d "%~dp0"
echo Stopping VillageVerse on ports 8000 and 5173...
call :KillPort 8000
call :KillPort 5173
echo Done. Close any VillageVerse API / UI windows if still open.
timeout /t 3
exit /b 0

:KillPort
set "_PORT=:%~1 "
for /f "tokens=5" %%P in ('netstat -ano ^| findstr "%_PORT%" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%P >nul 2>&1
)
exit /b 0
