@echo off
setlocal
cd /d "%~dp0"
python chatbot.py --interactive
if errorlevel 1 (
  echo.
  echo The chatbot could not start. Confirm that Python 3.10 or newer is installed.
)
pause
