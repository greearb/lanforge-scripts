
:: Initialize variables
echo Batch started
set "url="
set "server="
set "duration="
set "args="




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
if "%~1"=="--server" (
    set "server=%~2"
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




echo Batch started1


:argsParsed
set "args="
if defined url set "args=%args% --url %url%"
if defined server set "args=%args% --server %server%"
if defined duration set "args=%args% --duration %duration%"




echo Running with arguments: %args%
py real_browser.py %args%


:: Cleanup browser processes before execution
echo Cleaning up browser processes...
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM chromedriver.exe /T >nul 2>&1
echo Browser processes terminated.