@echo off
title Ollama Server
set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"

echo Checking Ollama on port 11434...
netstat -ano | findstr ":11434 " | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo.
    echo  Ollama is ALREADY running. Good to go!
    echo  API: http://localhost:11434
    echo.
    echo  You do NOT need this window. Close it and use VillageVerse:
    echo  - Run-VillageVerse.bat
    echo  - Dashboard - Reset ^& Seed - Run 1 Tick
    echo.
    pause
    exit /b 0
)

if not exist "%OLLAMA_EXE%" (
    echo Ollama not found. Install from https://ollama.com/download
    echo Or open the Ollama app from the Start menu.
    pause
    exit /b 1
)

echo Starting Ollama...
echo Keep this window open while running simulation ticks.
echo.
"%OLLAMA_EXE%" serve
pause
