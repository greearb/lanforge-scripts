# Variables
$WATCH_DIR = (Get-Location).Path  # Directory to watch (current directory)
$HOST_FILE = "zoom_host.py"      # Host file to watch for (Python script)
$CLIENT_FILE = "zoom_client.py"  # Client file to watch for if the host file is not found

# Function to watch for the file
function Watch-ForFile {
    while ($true) {
        if (Test-Path "$WATCH_DIR\$HOST_FILE") {
            Write-Host "Host file detected: $HOST_FILE in $WATCH_DIR"
            Execute-AndCleanup -FileToExecute $HOST_FILE -ExecutionType "host"
        } elseif (Test-Path "$WATCH_DIR\$CLIENT_FILE") {
            Write-Host "Client file detected: $CLIENT_FILE in $WATCH_DIR"
            Execute-AndCleanup -FileToExecute $CLIENT_FILE -ExecutionType "client"
        } else {
            Write-Host "No target files found in $WATCH_DIR. Retrying in 5 seconds..."
        }
        Start-Sleep -Seconds 5
    }
}



# Function to execute the script, handle errors, delete it, and perform necessary cleanup
function Execute-AndCleanup {
    param (
        [string]$FileToExecute,
        [string]$ExecutionType
    )
    # Try removing all chrome instances
    $taskkillCommand1 = "taskkill /F /IM chrome.exe /T"
    $taskkillCimmand2 = "taskkill /F /IM chromedriver.exe /T"
    Invoke-Expression -Command $taskkillCommand1
    $cmd_execution = $LASTEXITCODE -eq 0
    if (-not $cmd_execution) {
        Write-Host "No Chrome drivers are closed"
    } else {
        Write-Host "chrome drivers are closed"
    }
    
    Invoke-Expression -Command $taskkillCimmand2
    $cmd_execution = $LASTEXITCODE -eq 0
    if (-not $cmd_execution) {
        Write-Host "No chromium drivers are closed"
    } else {
        Write-Host "chromium drivers are closed"
    }
    # Try executing the script
    & py "$WATCH_DIR\$FileToExecute"
    $executionSuccess = $LASTEXITCODE -eq 0
    
    if (-not $executionSuccess) {
        Write-Host "Execution failed: $FileToExecute. Proceeding with cleanup..."
    } else {
        Write-Host "Successfully executed the script: $FileToExecute"
    }

    # Always attempt to delete the script file regardless of execution success
    if (Test-Path "$WATCH_DIR\$FileToExecute") {
        Remove-Item "$WATCH_DIR\$FileToExecute"
        Write-Host "Deleted the script: $FileToExecute"
    } else {
        Write-Host "Script file already removed: $FileToExecute"
    }

    
    
        $MeetingLinkFile = "$WATCH_DIR\credentials.csv"
        if (Test-Path $MeetingLinkFile) {
            Remove-Item $MeetingLinkFile
            Write-Host "Deleted the credentials file: $MeetingLinkFile"
        } else {
            Write-Host "No credentials file found to delete."
        }
    

    # Ensure that script continues even if there was an error
    if (-not $executionSuccess) {
        Write-Host "Continuing script execution after error."
    }
}

# Start watching for the file
Watch-ForFile




