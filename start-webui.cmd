@echo off
REM Start Hermes WebUI (native Windows). Opens http://127.0.0.1:8787
REM Optionally set HERMES_WEBUI_PASSWORD first to enable login.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0hermes-webui\start.ps1"
