@echo off
rem This script starts the VaPyNotes application.
rem It automatically changes to the script's directory and runs the app
rem using pythonw.exe to avoid opening a console window.

rem Change the current directory to the script's location
cd /d "%~dp0"

rem Start the application without a console window
start "VaPyNotes" .\.venv\Scripts\pythonw.exe main.py