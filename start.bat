@echo off
cd /d "%~dp0"
py -3 clicker.py
if errorlevel 1 (
  echo.
  echo Memo could not start. Install Python 3 from python.org with Tcl/Tk and the Python launcher enabled.
  pause
)
