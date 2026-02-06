# ================================
# open_env_and_wsl.ps1
# # One-time
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Run
# .\open_env_and_wsl.ps1
# ================================

$currentPath = $MyInvocation.MyCommand.Path
$scriptDirectory = Split-Path -Parent $currentPath

$projectDir = $scriptDirectory
$windowCount = 2

function Convert-WindowsPathToWSLPath {
    param (
        [string]$windowsPath
    )

    # Extract the drive letter
    $driveLetter = $windowsPath.Substring(0, 2).TrimEnd(':')

    # Replace backslashes with forward slashes
    $wslPath = $windowsPath -replace '\\', '/'

    # Format the WSL path
    $wslPath = "/mnt/$($driveLetter.ToLower())" + $wslPath.Substring(2)

    return $wslPath
}

function Open-WSLWithVenv {
    param (
        [string]$Directory,
        [int]$TerminalNumber
    )

    # Example usage
    # $windowsPath = "C:\Users\chuck\Documents"
    $windowsPath = $projectDir
    $wslPath = Convert-WindowsPathToWSLPath -windowsPath $windowsPath
    Write-Output $wslPath  # Outputs: /mnt/c/users/YourName

    Write-Output $projectDir

    # Command to run inside WSL:
    #   1. cd into your project directory
    #   2. start bash using the venv's activate script as its rcfile
    $wslCommand = "cd $wslPath; exec bash --rcfile ../.venv/bin/activate"

    # Launch WSL directly with the command, and set window title including terminal number
    $title = "WSL + venv #$TerminalNumber"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", " `$host.UI.RawUI.WindowTitle = '$title'; wsl bash -c '$wslCommand' "
}

for ($i = 1; $i -le $windowCount; $i++) {
    Open-WSLWithVenv -Directory $projectDir -TerminalNumber $i
}
