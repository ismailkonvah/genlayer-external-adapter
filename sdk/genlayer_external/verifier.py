
import base64
import os
from typing import Optional

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

_cached_public_key_pem: Optional[bytes] = None


def reset_public_key_cache() -> None:
    global _cached_public_key_pem
    _cached_public_key_pem = None


def _load_public_key_pem(relay_url: Optional[str] = None) -> bytes:
    global _cached_public_key_pem

    if _cached_public_key_pem is not None:
        return _cached_public_key_pem

    pem = os.getenv("GENLAYER_PUBLIC_KEY_PEM")
    path = os.getenv("GENLAYER_PUBLIC_KEY_PATH")

    if pem:
        _cached_public_key_pem = pem.encode("utf-8")
        return _cached_public_key_pem

    if path:
        with open(path, "rb") as f:
            _cached_public_key_pem = f.read()
        return _cached_public_key_pem

    if not relay_url:
        raise ValueError("relay_url is required when no public key env/path is configured")

    response = requests.get(f"{relay_url}/public-key", timeout=10)
    response.raise_for_status()
    payload = response.json()
    _cached_public_key_pem = payload["public_key_pem"].encode("utf-8")
    return _cached_public_key_pem


def verify_signature(message: bytes, signature_b64: str, relay_url: Optional[str] = None) -> bool:
    try:
        public_key_pem = _load_public_key_pem(relay_url=relay_url)
        public_key = serialization.load_pem_public_key(public_key_pem)
        if not isinstance(public_key, Ed25519PublicKey):
            return False
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, message)
        return True
    except Exception:
        return False
