@echo off
cd /d "%~dp0"
cd ..
git add *
git commit -m "auto commit 2"
git push origin main
