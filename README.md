<h1 align="center">
  <br>
  <a href="https://github.com/3ct0s/"><img src="https://i.ibb.co/K0RqpVb/disctopia.png" width=600 weigth=500 alt="Disctopia"></a>
  <br>
  Disctopia
  <br>
</h1>

<h4 align="center">Disctopia Command and Control</h4>

<p align="center">
    <img src="https://img.shields.io/badge/Backdoor_Platform-Windows-blue">
    <img src="https://img.shields.io/badge/Version-2.1.1-blue">
    <img src="https://img.shields.io/badge/Python-3.8.9-blue">
</p>

---

## What is Disctopia?

Disctopia is a malware generator that generates backdoors which use online platforms as C2s. This includes, Discord, Telegram and Github. 

Our goal is to prove that anything can be a C2, if you want to :) ...

## How does it work?

The disctopia backdoors are using libraries which allow the backdoor to act as a "Bot" for the above mentioned platorms. Essentially the attacker contacts the bot and the specifies a malicious command to execute on the target "Agent". 

Disctopia is equiped with a lot of features **some** of which are:
- Encrypted traffic (HTTPS)
- Running system commands on target Agent
- Keylogger (Limited to Discord)
- Grabbing webcam snaps
- Multiple online agents a time (Limited to Discord & GitHub)

## Installation and Usage

Disctopia is better installed and used on Kali Linux:
```
git clone https://github.com/3ct0s/disctopia-c2
cd ./disctopia-c2
chmod +x setup.sh
./setup.sh
```
Once this is done we can use the builder. Lets build a discord based C2 backdoor:
```
python builder.py
use discord
set name <backdoor-name>
set guild-id <server id from discord>
set bot-token <discord bot token>
set channel-id <channel id from discord server>
set webhook <discord webhook>
build
```

## How to Setup Disctopia
Since the setup process is very specific for each platform:

> Please follow the [setup guide](https://github.com/3ct0s/disctopia-c2/wiki/) to setup Disctopia.

## Contributors
Contributions are welcome to our GitHub repo! We value community involvement and appreciate all types of contributions, from bug reports to code. Join us in building something great and making a positive impact on the world. Get involved today!

## Disclaimer
This github repository is made for educational purposes only. The developer is not responsible for any misuse of this software. **Do not use this software for illegal purposes.**
