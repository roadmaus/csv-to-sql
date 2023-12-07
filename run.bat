
REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 echo Failed to activate virtual environment! && exit /b %errorlevel%

REM Run the Python script
echo Running Python script...
python gui.py
if %errorlevel% neq 0 echo Python script encountered an error! && exit /b %errorlevel%

REM Optional: deactivate the virtual environment when done
echo Deactivating virtual environment...
call deactivate
if %errorlevel% neq 0 echo Failed to deactivate virtual environment!

echo Script execution completed.
