# Before you can run this script, start with:
#
# 	Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy UnRestricted
#
#
# You want to install Chocolatey as Administrator, so 
# Right-click on your Posh icon, Run as Administrator
# then .\setup_lanforge_python.ps1
#

# set this if you need set -e behavior
# $ErrorActionPreference = "Stop"

# $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
# $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

#Requires -RunAsAdministrator
Set-ExecutionPolicy -Scope CurrentUser UnRestricted

$testchoco = powershell choco -v
# & $testchoco
if ($lastexitcode -ne 0){
    Write-Output "Seems Chocolatey is not installed, installing now"
    Set-ExecutionPolicy Bypass -Scope Process -Force
	[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
	iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
	choco upgrade chocolatey
	Write-Output "Re-run this script now that Chocolatey is installed."
	exit
}
else{
    Write-Output "Chocolatey Version $testchoco is already installed"
}

choco install microsoft-windows-terminal
refreshenv
choco install git.install
RefreshEnv.cmd
$env:PATH += ";C:\Program Files\Git\bin"
$testgit = powershell git --version
if ($lastexitcode -ne 0){
	Write-Output "git was not installed or is not in your path, bye."
	exit 1
}

choco install -y python3
RefreshEnv.cmd
$testpy = powershell python --version
if ($lastexitcode -ne 0){
	Write-Output "git was not installed or is not in your path, bye."
	exit 1
}

python -m pip install --upgrade pip

cd $Home\Documents
if (-not(test-path "$Home\Documents\lanforge-scripts")) {
	git clone 'https://github.com/greearb/lanforge-scripts'
}

if (-not(test-path "$Home\Documents\venv_lanforge")) {
	mkdir venv_lanforge
	python -m venv_lanforge
	if ($lastexitcode -ne 0) {
		Write-Output "Problems creating python virtual environment, bye."
		exit 1
	}
}
if (-not(test-path ".\venv_lanforge\Scripts\Activate")) {
	Write-Output "No virtual python environment to activate, bye."
	exit 1
}
.\venv_lanforge\Scripts\Activate

cd $Home\Documents\lanforge-scripts
python .\update_dependencies.py

