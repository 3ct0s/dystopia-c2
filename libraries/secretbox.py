# -*- coding: utf-8 -*-
"""Runtime secret unlock for Dystopia agents.

Build-time tooling (libraries/obfuscate_build.py) fills the fragment
placeholders below with per-build key material. Plaintext Discord secrets
must never appear in packaged agent source.
"""

from __future__ import annotations

import base64
import hashlib

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:  # fail closed
    raise SystemExit(
        "[!] cryptography is required to unlock agent secrets "
        "(pip install cryptography)"
    ) from exc

# --- key fragments (replaced per build; do not hand-edit) ---
_F0 = bytes.fromhex("{F0_HEX}")
_F1 = bytes.fromhex("{F1_HEX}")
_F2 = bytes.fromhex("{F2_HEX}")
_XOR = {XOR_INT}
_SALT = bytes.fromhex("{SALT_HEX}")


def _assemble_key() -> bytes:
    """Assemble AES-256 key from scattered constants + light transforms."""
    if len(_F0) != 16 or len(_F1) != 16 or len(_F2) != 16:
        raise RuntimeError("secretbox key material incomplete")
    buf = bytearray(32)
    for i in range(16):
        buf[i] = _F0[i] ^ _F1[i] ^ (_XOR & 0xFF)
        buf[16 + i] = _F2[i] ^ ((_F0[i] + _F1[i]) & 0xFF) ^ ((_XOR >> 8) & 0xFF)
    # Mix with salt via SHA-256 so fragments alone are not the final key.
    return hashlib.sha256(bytes(buf) + _SALT + b"dystopia-sb-v1").digest()


def unlock(blob: str) -> str:
    """Decrypt a build-time AES-256-GCM blob (base64: nonce||ciphertext)."""
    if not blob or blob.startswith("{") and blob.endswith("}"):
        raise RuntimeError("secretbox placeholder not filled by builder")
    raw = base64.b64decode(blob.encode("ascii"), validate=True)
    if len(raw) < 13:
        raise RuntimeError("secretbox blob too short")
    nonce, ct = raw[:12], raw[12:]
    pt = AESGCM(_assemble_key()).decrypt(nonce, ct, None)
    return pt.decode("utf-8")
