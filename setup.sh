#!/usr/bin/env bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	FILE=/etc/lsb-release
	if test -f "$FILE"; then
		echo "/etc/lsb-release exists"
		export DISTRIB=$(awk -F= '/^DISTRIB_ID/{print $2}' /etc/lsb-release | tr -d \")
	else	
		export DISTRIB="Not Arch"
		echo "/etc/lsb-release doesn't exist"
	fi
	
	if [[ ${DISTRIB} = "Arch"* || ${DISTRIB} = "ManjaroLinux"* ]]; then
		sudo pacman -Syyu
		sudo pacman -S base-devel --needed
		sudo pacman -S yay --noconfirm
		yay -S python38
		sudo pacman -S python-pip --noconfirm 
		sudo pip3 install -r requirements.txt
		sudo pacman -S wine --noconfirm
	else
		rm /var/lib/dpkg/lock
		rm /var/cache/apt/archives/lock
		rm /var/lib/apt/lists/lock
		sudo dpkg --add-architecture i386
		sudo apt-get update
		sudo apt-get install python3.9 -y
		sudo apt-get install python3-pip -y
		sudo pip3 install -r requirements.txt
		sudo apt-get install -y wine
	fi  
FILE=python-3.8.9.exe
if test -f "$FILE"; then
	echo "$FILE already exists."
else
	sudo wget https://www.python.org/ftp/python/3.8.9/python-3.8.9.exe
fi
arg1=$1
arg2="-s"
if [ "$arg1" == "$arg2" ]; then
	echo "Beginning silent Python 3.8.9 Installation"
	sudo wine cmd /c python-3.8.9.exe /quiet InstallAllUsers=0
else
	sudo wine cmd /c python-3.8.9.exe
fi
if [[ ${DISTRIB} = "Arch"* || ${DISTRIB} = "ManjaroLinux"* ]]; then
	sudo wine "/root/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python38-32/python.exe" -m pip install psutil keyboard==0.13.5 pywin32==303 pycryptodome==3.12.0 pyautogui==0.9.53 pyinstaller discord_webhook==0.14.0 discord.py opencv-python==4.5.3.56 sounddevice scipy==1.9.0
elif [[ ${DISTRIB} = "Not Arch"* ]]; then
	sudo wine "/root/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python38-32/python.exe" -m pip install psutil keyboard==0.13.5 pywin32==303 pycryptodome==3.12.0 pyautogui==0.9.53 pyinstaller==5.3 discord_webhook==0.14.0 discord.py opencv-python==4.5.3.56 sounddevice scipy==1.9.0
fi
fi
echo "Done"
