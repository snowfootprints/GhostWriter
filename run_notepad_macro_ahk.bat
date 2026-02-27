@echo off
cd /d "%~dp0"

echo [1/2] Checking AutoHotkey v2...
set "AHK_EXE="
if exist "%ProgramFiles%\AutoHotkey\v2\AutoHotkey64.exe" set "AHK_EXE=%ProgramFiles%\AutoHotkey\v2\AutoHotkey64.exe"
if not defined AHK_EXE if exist "%ProgramFiles%\AutoHotkey\AutoHotkey64.exe" set "AHK_EXE=%ProgramFiles%\AutoHotkey\AutoHotkey64.exe"
if not defined AHK_EXE if exist "%ProgramFiles(x86)%\AutoHotkey\v2\AutoHotkeyU64.exe" set "AHK_EXE=%ProgramFiles(x86)%\AutoHotkey\v2\AutoHotkeyU64.exe"
if not defined AHK_EXE if exist "%LOCALAPPDATA%\Programs\AutoHotkey\v2\AutoHotkey64.exe" set "AHK_EXE=%LOCALAPPDATA%\Programs\AutoHotkey\v2\AutoHotkey64.exe"
if not defined AHK_EXE if exist "%LOCALAPPDATA%\Programs\AutoHotkey\v2\AutoHotkey32.exe" set "AHK_EXE=%LOCALAPPDATA%\Programs\AutoHotkey\v2\AutoHotkey32.exe"
if not defined AHK_EXE if exist "%LOCALAPPDATA%\Programs\AutoHotkey\UX\AutoHotkeyUX.exe" set "AHK_EXE=%LOCALAPPDATA%\Programs\AutoHotkey\UX\AutoHotkeyUX.exe"

if not defined AHK_EXE (
  echo AutoHotkey v2 is not installed.
  echo Install command ^(PowerShell^): winget install AutoHotkey.AutoHotkey
  echo Download page: https://www.autohotkey.com/
  pause
  exit /b 1
)

echo [2/2] Running notepad_macro.ahk...
"%AHK_EXE%" "%~dp0notepad_macro.ahk"
