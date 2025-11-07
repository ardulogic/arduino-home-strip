@echo off
echo Building HomeStripMonitor executable...
echo.

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Convert icon.png to icon.ico if needed
if exist icon.png if not exist icon.ico (
    echo Converting icon.png to icon.ico...
    python convert_icon.py
)

REM Build the executable
if exist icon.ico (
    pyinstaller --onefile --name HomeStripMonitor --windowed --icon icon.ico --hiddenimport serial --hiddenimport serial.tools --hiddenimport serial.tools.list_ports --hiddenimport serial.win32 --hiddenimport pystray --hiddenimport PIL --hiddenimport PIL.Image --add-data "config.py;." --add-data "icon.png;." pc_monitor.py
) else if exist icon.png (
    pyinstaller --onefile --name HomeStripMonitor --windowed --icon icon.png --hiddenimport serial --hiddenimport serial.tools --hiddenimport serial.tools.list_ports --hiddenimport serial.win32 --hiddenimport pystray --hiddenimport PIL --hiddenimport PIL.Image --add-data "config.py;." --add-data "icon.png;." pc_monitor.py
) else (
    pyinstaller --onefile --name HomeStripMonitor --windowed --hiddenimport serial --hiddenimport serial.tools --hiddenimport serial.tools.list_ports --hiddenimport serial.win32 --hiddenimport pystray --hiddenimport PIL --hiddenimport PIL.Image --add-data "config.py;." pc_monitor.py
)

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

