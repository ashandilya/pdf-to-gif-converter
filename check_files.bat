@echo off
echo Checking files in the current directory...
echo.

dir /b
echo.

echo If you don't see the expected files, there might be an issue with file permissions or the file system.
echo.

echo Press any key to open the diagnostic page in your default browser...
pause > nul

start diagnostic.html

echo.
echo If the diagnostic page doesn't open automatically, please open it manually.
echo.

pause 