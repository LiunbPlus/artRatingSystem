@echo off
setlocal

cd /d "%~dp0"
cd ..
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%CD%\tools\start-windows.ps1" %*
exit /b %ERRORLEVEL%
