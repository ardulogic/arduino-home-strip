@echo off
echo Building HomeStripMonitor executable...
echo.

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Build the executable
pyinstaller --onefile --name HomeStripMonitor --console --add-data "config.py;." pc_monitor.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build successful!
echo Executable location: dist\HomeStripMonitor.exe
echo ========================================
echo.
pause

