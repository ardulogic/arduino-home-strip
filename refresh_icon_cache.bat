@echo off
echo Refreshing Windows icon cache...
echo.

REM Stop Windows Explorer
taskkill /f /im explorer.exe >nul 2>&1

REM Clear icon cache
del /a /q "%localappdata%\IconCache.db" >nul 2>&1
del /a /f /q "%localappdata%\Microsoft\Windows\Explorer\iconcache*" >nul 2>&1

REM Restart Windows Explorer
start explorer.exe

echo.
echo Icon cache cleared. The icon should appear after refreshing the folder (F5).
echo.
pause

