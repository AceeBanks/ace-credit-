@echo off
rem start_grant_agent.cmd - convenience launcher for the Grant Agent.
rem Usage:
rem   start_grant_agent.cmd          run API on :8000   (open http://127.0.0.1:8000/docs)
rem   start_grant_agent.cmd web      run API + chat UI on :3000
rem   start_grant_agent.cmd stop     stop processes started by the launcher
rem   start_grant_agent.cmd status   show what is running
setlocal
set "SGA_DIR=%~dp0"
if /i "%~1"=="web"      powershell -NoProfile -ExecutionPolicy Bypass -File "%SGA_DIR%start_grant_agent.ps1" -Web
if /i "%~1"=="stop"     powershell -NoProfile -ExecutionPolicy Bypass -File "%SGA_DIR%start_grant_agent.ps1" -Stop
if /i "%~1"=="status"   powershell -NoProfile -ExecutionPolicy Bypass -File "%SGA_DIR%start_grant_agent.ps1" -Status
if /i "%~1"==""         powershell -NoProfile -ExecutionPolicy Bypass -File "%SGA_DIR%start_grant_agent.ps1"
endlocal