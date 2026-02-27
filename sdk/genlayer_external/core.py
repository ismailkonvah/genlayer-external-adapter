
import hashlib
import json
import os
import time
import uuid

import requests

from .exceptions import RelayResponseError, RelaySignatureError
from .verifier import verify_signature

RELAY_URL = os.getenv("GENLAYER_RELAY_URL", "http://localhost:8000")

def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))

def relay_call(endpoint: str, payload: dict):
    secured_payload = {
        **payload,
        "nonce": uuid.uuid4().hex,
        "request_timestamp": int(time.time()),
    }

    response = requests.post(f"{RELAY_URL}/{endpoint}", json=secured_payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    signature = data.pop("signature", None)
    if not signature:
        raise RelayResponseError("Relay response missing signature")
    canonical = canonical_json(data)
    hash_bytes = hashlib.sha256(canonical.encode()).digest()

    if not verify_signature(hash_bytes, signature, relay_url=RELAY_URL):
        raise RelaySignatureError("Invalid relay signature")

    return data
