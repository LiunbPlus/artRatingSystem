@echo off
setlocal

cd /d "%~dp0"
cd ..

set "PROJECT_DIR=%CD%"
set "BACKEND_DIR=%PROJECT_DIR%\backend"
set "FRONTEND_DIR=%PROJECT_DIR%\frontend"
set "PYTHON_EXE=%BACKEND_DIR%\venv\Scripts\python.exe"

start "Art Rating System - Backend" /D "%BACKEND_DIR%" cmd.exe /d /k ""%PYTHON_EXE%" main.py"
start "Art Rating System - Frontend" /D "%FRONTEND_DIR%" cmd.exe /d /k npm.cmd run dev

endlocal
