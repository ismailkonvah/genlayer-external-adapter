
import base64
import hashlib
import json
import os
import time
from typing import Dict

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import FastAPI, HTTPException

from .providers import load_price_provider, load_weather_provider
from .schemas import PriceRequest, WeatherRequest

app = FastAPI()
weather_provider = load_weather_provider()
price_provider = load_price_provider()

MAX_SKEW_SECONDS = int(os.getenv("GENLAYER_MAX_SKEW_SECONDS", "300"))
_used_nonces: Dict[str, int] = {}

def _load_private_key() -> Ed25519PrivateKey:
    pem = os.getenv("GENLAYER_PRIVATE_KEY_PEM")
    path = os.getenv("GENLAYER_PRIVATE_KEY_PATH")

    if pem:
        key_bytes = pem.encode("utf-8")
    elif path:
        with open(path, "rb") as f:
            key_bytes = f.read()
    else:
        # Development fallback only; use env-based key material in production.
        return Ed25519PrivateKey.generate()

    key = serialization.load_pem_private_key(key_bytes, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("GENLAYER private key must be Ed25519")
    return key


private_key = _load_private_key()

def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def sign_message(message: bytes) -> str:
    signature = private_key.sign(message)
    return base64.b64encode(signature).decode()


def _validate_timestamp(request_timestamp: int) -> None:
    now = int(time.time())
    if abs(now - request_timestamp) > MAX_SKEW_SECONDS:
        raise HTTPException(status_code=400, detail="Request timestamp outside freshness window")


def _cleanup_nonces(now: int) -> None:
    expired = [nonce for nonce, ts in _used_nonces.items() if (now - ts) > MAX_SKEW_SECONDS]
    for nonce in expired:
        _used_nonces.pop(nonce, None)


def _register_nonce(endpoint: str, nonce: str, request_timestamp: int) -> None:
    _validate_timestamp(request_timestamp)
    now = int(time.time())
    _cleanup_nonces(now)

    scoped_nonce = f"{endpoint}:{nonce}"
    if scoped_nonce in _used_nonces:
        raise HTTPException(status_code=409, detail="Replay detected: nonce already used")

    _used_nonces[scoped_nonce] = now


def get_public_key_pem() -> str:
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem.decode("utf-8")


@app.get("/public-key")
def public_key() -> dict:
    return {"public_key_pem": get_public_key_pem()}

@app.post("/weather")
def weather(payload: WeatherRequest):
    _register_nonce("weather", payload.nonce, payload.request_timestamp)
    temperature = weather_provider.get_temperature(payload.city)

    data = {
        "city": payload.city,
        "temperature": temperature,
        "timestamp": int(time.time()),
    }

    canonical = canonical_json(data)
    hash_bytes = hashlib.sha256(canonical.encode()).digest()
    signature = sign_message(hash_bytes)

    data["signature"] = signature
    return data

@app.post("/price")
def price(payload: PriceRequest):
    _register_nonce("price", payload.nonce, payload.request_timestamp)
    price_value = price_provider.get_price(payload.symbol)

    data = {
        "symbol": payload.symbol,
        "price": price_value,
        "timestamp": int(time.time()),
    }

    canonical = canonical_json(data)
    hash_bytes = hashlib.sha256(canonical.encode()).digest()
    signature = sign_message(hash_bytes)

    data["signature"] = signature
    return data
