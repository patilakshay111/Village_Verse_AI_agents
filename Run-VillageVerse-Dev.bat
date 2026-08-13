@echo off
REM Hot-reload UI on :5173 — run Run-VillageVerse.bat first for the API
start "VillageVerse UI Dev" cmd /k "cd /d "%~dp0frontend" && npm run dev"
echo Dev UI: http://127.0.0.1:5173  (API should be on :8000)
