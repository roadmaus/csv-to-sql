@echo off

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Python script
python gui.py

REM Optional: deactivate the virtual environment when done
call deactivate
