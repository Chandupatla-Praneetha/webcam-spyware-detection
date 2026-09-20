@echo off
REM Double-click this file to launch Webcam Spyware Detection.
REM Uses the virtual environment in .\venv so it works even if your
REM system Python doesn't have bcrypt / opencv-contrib-python / etc installed.
REM
REM First-time setup (only needed once):
REM   python -m venv venv
REM   venv\Scripts\activate
REM   python -m pip install -r requirements.txt

cd /d "%~dp0"

if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" main.py
) else (
    echo venv not found -- falling back to system Python.
    echo Run setup first: python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    start "" pythonw main.py
)
