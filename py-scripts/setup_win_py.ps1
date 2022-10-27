# setup_lanforge_python2.ps1
# use this script after the installation part is done

Set-Location $Home\Documents
if (-not(test-path "$Home\Documents\lanforge-scripts")) {
	git clone 'https://github.com/greearb/lanforge-scripts'
}

if (-not(test-path "$Home\Documents\venv_lanforge\Scripts\Activate")) {
	# mkdir venv_lanforge
   Write-Output "Creating virtual environment..."
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

Set-Location $Home\Documents\lanforge-scripts\py-scripts
python .\update_dependencies.py

#