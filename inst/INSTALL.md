# Disctopia Installation Guide

You need to clone the repository with the command
```
git clone https://github.com/3ct0s/disctopia-c2.git
```
Next you need to cd into the cloned project files, run a command to fix an error and create a new setup file, change the permissions of the setup-new.sh file and run it.

### Windows
```
cd disctopia-c2
powershell.exe -ExecutionPolicy Bypass -Command .\setup.ps1
```
### Linux
```
cd disctopia-c2
sed $'s/\r$//' ./setup.sh > ./setup-new.sh 
chmod +x setup-new.sh
sudo ./setup-new.sh
```
You will be asked to say **yes** or **no** while installing the needed dependencies. Make sure you select **yes** and press enter.

![image](https://i.ibb.co/GVHVYdZ/Capture.png)


You will also be asked to install **Python 3.8.9**, please click on **"Install Now"** and **"Close"** when the installation is done

![image](https://i.ibb.co/f82KVNS/Capture.png)

Once you are done with the installation you can move to the next step which is setting up the bot.

## Setup Disctopia

Follow the [setup guide](SETUP.md) to setup Disctopia.
