#!/usr/bin/env bash

# Determine OS type
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Check if /etc/lsb-release exists
    FILE=/etc/lsb-release
    if [[ -f "$FILE" ]]; then
        echo "/etc/lsb-release exists"
        export DISTRIB=$(awk -F= '/^DISTRIB_ID/{print $2}' /etc/lsb-release | tr -d \")
    else
        export DISTRIB="Not Arch"
        echo "/etc/lsb-release doesn't exist"
    fi

    # Arch-based distributions
    if [[ ${DISTRIB} == "Arch"* || ${DISTRIB} == "ManjaroLinux"* ]]; then
        sudo pacman -Syyu
        sudo pacman -S base-devel --needed
        sudo pacman -S yay --noconfirm
        yay -S python38
        sudo pacman -S python-pip --noconfirm 
        sudo pip3 install -r requirements.txt
        sudo pacman -S wine --noconfirm

    # Debian-based distributions
    else
        sudo rm -f /var/lib/dpkg/lock
        sudo rm -f /var/cache/apt/archives/lock
        sudo rm -f /var/lib/apt/lists/lock
        sudo dpkg --add-architecture i386
        sudo apt-get update
        sudo apt-get install python3.9 -y
        sudo apt-get install python3-pip -y
        sudo pip3 install -r requirements.txt
        sudo apt-get install -y wine
    fi

    # Download Python 3.8.9 installer if not exists
    FILE=python-3.8.9.exe
    if [[ -f "$FILE" ]]; then
        echo "$FILE already exists."
    else
        sudo wget https://www.python.org/ftp/python/3.8.9/python-3.8.9.exe --no-check-certificate
    fi

    # Determine installation mode (silent or not)
    arg1=$1
    arg2="-s"
    if [[ "$arg1" == "$arg2" ]]; then
        echo "Beginning silent Python 3.8.9 Installation"
        sudo wine cmd /c python-3.8.9.exe /quiet InstallAllUsers=0
    else
        sudo wine cmd /c python-3.8.9.exe
    fi

    # Install necessary Python packages using wine
    PYTHON_EXE="/root/.wine/drive_c/users/root/Local Settings/Application Data/Programs/Python/Python38-32/python.exe"
    if [[ ! -f "$PYTHON_EXE" ]]; then
        PYTHON_EXE="/root/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python38-32/python.exe"
    fi

    sudo wine "$PYTHON_EXE" -m pip install pillow==8.3.2 pyscreeze==0.1.28 pyautogui==0.9.52 psutil keyboard==0.13.5 pywin32==303 pycryptodome==3.12.0 pyinstaller==5.3 discord_webhook==0.14.0 discord.py opencv-python==4.5.3.56 sounddevice scipy==1.9.0 pyTelegramBotAPI PyGithub
fi

echo "Done"
