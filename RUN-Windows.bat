@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Yadakpakhsh Shop - Django
chcp 65001 >nul 2>nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set "PYCMD="

echo.
echo  ===========================================
echo    Yadakpakhsh shop - starting...
echo  ===========================================
echo.

if not exist "setup_and_run.py" goto :noextract

call :try "py -3.12"
call :try "py -3.11"
call :try "py -3.13"
call :try "py -3.10"
call :try "py -3.9"
call :try "py -3.8"
call :try "py -3"
call :try "python"
call :try "python3"
if not defined PYCMD call :findlocal
if not defined PYCMD goto :nopython
goto :run

:try
if defined PYCMD goto :eof
%~1 -c "import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)" >nul 2>nul
if not errorlevel 1 set "PYCMD=%~1"
goto :eof

:findlocal
for %%V in (312 311 313 310 39 38) do call :trypath "%LocalAppData%\Programs\Python\Python%%V\python.exe"
for %%V in (312 311 313 310 39 38) do call :trypath "%ProgramFiles%\Python%%V\python.exe"
goto :eof

:trypath
if defined PYCMD goto :eof
if exist %1 set PYCMD=%1
goto :eof

:noextract
echo  ERROR: setup_and_run.py was not found next to this file.
echo.
echo  You probably ran this file from INSIDE the zip.
echo  Right-click the zip file ^> "Extract All..." ^> then open the extracted folder
echo  and double-click RUN-Windows.bat again.
goto :fail

:nopython
echo  Python 3 was not found on this computer.
where winget >nul 2>nul
if errorlevel 1 goto :manual
echo.
echo  Trying to install Python 3.12 automatically (this needs internet)...
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
call :findlocal
if defined PYCMD goto :run
:manual
echo.
echo  Please install Python from:  https://www.python.org/downloads/
echo  IMPORTANT: on the first installer screen tick "Add python.exe to PATH".
echo  Then run this file again.
start "" https://www.python.org/downloads/
goto :fail

:run
echo  Using Python: %PYCMD%
echo.
%PYCMD% setup_and_run.py
if errorlevel 1 goto :fail
goto :end

:fail
echo.
echo  ----- Something went wrong. Take a screenshot of this window and send it. -----

:end
echo.
pause
endlocal
