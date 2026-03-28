@echo off
REM Build battery_monitor into a single Windows exe.
REM Run this from the d:\battery-monitor\ directory.
REM Output: dist\battery_monitor.exe

pyinstaller ^
  --onefile ^
  --windowed ^
  --name battery_monitor ^
  battery_monitor\main.py

echo.
echo Build complete. Exe is at: dist\battery_monitor.exe
echo.
echo To install: copy dist\battery_monitor.exe to a permanent location
echo (e.g. %LOCALAPPDATA%\BatteryMonitor\battery_monitor.exe)
echo then run it once so it writes its startup registry entry.
pause
