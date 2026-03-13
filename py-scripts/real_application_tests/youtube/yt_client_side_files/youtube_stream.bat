@echo off

:: Initialize variables
echo Batch started
set "url="
set "host="
set "port="
set "device_name="
set "duration="
set "args="
set "res="

:: Cleanup browser processes before execution
echo Cleaning up browser processes...
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM chromedriver.exe /T >nul 2>&1
echo Browser processes terminated.

timeout /t 5 /nobreak >nul
:: Parse command line arguments
:parseArgs
if "%~1"=="" goto argsParsed
if "%~1"=="--url" (
    set "url=%~2"
    shift
    shift
    goto parseArgs
)
if "%~1"=="--host" (
    set "host=%~2"
    shift
    shift
    goto parseArgs
)
if "%~1"=="--port" (
    set "port=%~2"
    shift
    shift
    goto parseArgs
)
if "%~1"=="--device_name" (
    set "device_name=%~2"
    shift
    shift
    goto parseArgs
)
if "%~1"=="--duration" (
    set "duration=%~2"
    shift
    shift
    goto parseArgs
)
if "%~1"=="--res" (
    set "res=%~2"
    shift
    shift
    goto parseArgs
)
shift
goto parseArgs

echo Batch started1

:argsParsed
set "args="
if defined url set "args=%args% --url %url%"
if defined host set "args=%args% --host %host%"
if defined port set "args=%args% --port %port%"
if defined device_name set "args=%args% --device_name %device_name%"
if defined duration set "args=%args% --duration %duration%"
if defined res set "args=%args% --res %res%"


echo Running with arguments: %args%
py youtube.py %args%

:: Cleanup browser processes before execution
echo Cleaning up browser processes...
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM chromedriver.exe /T >nul 2>&1
echo Browser processes terminated.