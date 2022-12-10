$pythonVersion = "3.8.9"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion.exe"
$pythonDownloadPath = "$(Get-Location)\python-$pythonVersion.exe"
$pythonInstallDir = "$(Get-Location)\python$pythonVersion"

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if (-not(Test-Path -Path $pythonDownloadPath -PathType Leaf)) {
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonDownloadPath
} else {
    Write-Host "$pythonDownloadPath already exists."
}

If ($args[0] -eq "-s"){
    Write-Host "Beginning silent Python $pythonVersion Installation"
    & $pythonDownloadPath /quiet InstallAllUsers=0 TargetDir=$pythonInstallDir | Out-Null
} else {
    & $pythonDownloadPath InstallAllUsers=0 TargetDir=$pythonInstallDir | Out-Null
}

& "$pythonInstallDir\python.exe" -m venv venv
& "$(Get-Location)\venv\Scripts\python.exe" -m pip install distro psutil keyboard==0.13.5 pywin32==303 pycryptodome==3.12.0 pyautogui==0.9.53 pyinstaller discord_webhook==0.14.0 discord.py prettytable opencv-python==4.5.3.56 sounddevice scipy==1.9.0
