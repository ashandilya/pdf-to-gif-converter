@echo off
echo Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing Python dependencies...
echo This may take a few minutes...
pip install --upgrade Pillow PyMuPDF

if errorlevel 1 (
    echo.
    echo Error: Failed to install dependencies
    echo.
    echo Trying alternative installation method...
    pip install --upgrade --no-cache-dir Pillow
    pip install --upgrade --no-cache-dir PyMuPDF
)

echo.
echo Starting the server...
start "PDF to GIF Server" python server.py

echo.
echo Waiting for server to start...
timeout /t 3 > nul

echo.
echo Opening the website...
start http://localhost:8000

echo.
echo The server is running at http://localhost:8000
echo.
echo If you see any errors in the server window, please:
echo 1. Close this window
echo 2. Close the server window
echo 3. Run 'pip install --upgrade Pillow PyMuPDF' in a new command prompt
echo 4. Try starting the server again
echo.
echo Press Ctrl+C in the server window to stop the server when you're done.
echo.
pause 