@echo off
setlocal
title Image Sorter

rem Folder this file is in (the drive root), with a trailing backslash.
set "ROOT=%~dp0"
set "MAIN=%ROOT%app\image-sorter\main.py"
set "PYTHONPATH=%ROOT%app\lib"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"

set "PYTHON=%ROOT%app\python\windows-x64\python.exe"
if exist "%PYTHON%" goto run

rem No bundled Python: fall back to one installed on this computer.
set "PYTHON="
for %%P in (python.exe py.exe) do if not defined PYTHON set "PYTHON=%%~$PATH:P"
if defined PYTHON goto run

echo Python was not found. Rebuild the drive with scripts\build_drive.py.
goto end

:run
rem "%ROOT%." avoids the trailing backslash escaping the closing quote.
"%PYTHON%" "%MAIN%" --root "%ROOT%." %*

:end
echo.
pause
