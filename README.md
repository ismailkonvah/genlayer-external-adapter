# GenLayer External Adapter SDK
[![Tests](https://github.com/ismailkonvah/genlayer-external-adapter/actions/workflows/tests.yml/badge.svg)](https://github.com/ismailkonvah/genlayer-external-adapter/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Deterministic external API adapter infrastructure for GenLayer Intelligent Contracts.

## Overview

Intelligent Contracts need off-chain data, but direct API calls can expose API keys and create validator divergence. This project provides a secure relay + SDK pattern where external results are normalized, signed, and verified.

Core value:

- Contracts never hold provider API keys.
- Relay signs canonical payload digests (SHA-256 + Ed25519).
- SDK verifies signatures before returning values to contract logic.
- Replay and stale requests are constrained with nonce + timestamp checks.

## Scope

- Python SDK package: `genlayer_external`
- FastAPI relay service
- Provider abstraction for weather/price/social backends
- Signed and verifiable adapter responses
- Replay and freshness protection
- Local tests + CI workflow

## Live Providers

- Weather: `open-meteo` (no key required)
- Price: `coingecko` (optional key via `COINGECKO_API_KEY`)
- Social: `reddit` (optional `REDDIT_USER_AGENT`)
- Local deterministic fallback: `mock`

## Architecture

Flow:

1. Intelligent Contract calls SDK function (`get_temperature`, `get_price`, `get_social_buzz`).
2. SDK sends payload with `nonce` + `request_timestamp` to relay.
3. Relay validates schema/freshness/replay constraints.
4. Relay fetches provider data and normalizes output deterministically.
5. Relay canonicalizes JSON and signs digest with Ed25519 private key.
6. SDK verifies signature using configured relay public key.

High-level path:

Intelligent Contract -> SDK -> Relay -> External API -> Signed Response -> Validator Verification

## Quickstart

1. Install dependencies:

```bash
pip install -e .
pip install -r relay_service/requirements.txt
```

2. (Optional, recommended) generate persistent relay keys:

```bash
python relay_service/generate_keys.py
```

3. Configure environment (PowerShell example):

```powershell
$env:GENLAYER_PRIVATE_KEY_PATH="relay_private_key.pem"
$env:GENLAYER_PUBLIC_KEY_PATH="relay_public_key.pem"
$env:GENLAYER_WEATHER_PROVIDER="open-meteo"
$env:GENLAYER_PRICE_PROVIDER="coingecko"
$env:GENLAYER_SOCIAL_PROVIDER="reddit"
# optional
$env:COINGECKO_API_KEY="your_key"
$env:REDDIT_USER_AGENT="genlayer-external-adapter/0.1"
```

4. Start relay:

```bash
uvicorn relay_service.main:app --reload --port 8000
```

5. Use SDK:

```python
from genlayer_external.weather import get_temperature
from genlayer_external.prices import get_price
from genlayer_external.social import get_social_buzz

print(get_temperature("London"))
print(get_price("ETH"))
print(get_social_buzz("genlayer", "reddit"))
```

## Endpoint Contracts

`POST /weather`

- Request: `city`, `nonce`, `request_timestamp`
- Response: `city`, `temperature`, `timestamp`, `signature`

`POST /price`

- Request: `symbol`, `nonce`, `request_timestamp`
- Response: `symbol`, `price`, `timestamp`, `signature`

`POST /social`

- Request: `platform` (currently `reddit`), `topic`, `nonce`, `request_timestamp`
- Response: `platform`, `topic`, `buzz_score`, `mentions`, `timestamp`, `signature`

## Security and Determinism

- Canonical JSON serialization (`sort_keys=True`, compact separators)
- SHA-256 digest signing
- Ed25519 signature verification in SDK
- Strict request schema validation (`extra=forbid`)
- Freshness validation (`GENLAYER_MAX_SKEW_SECONDS`)
- Endpoint-scoped nonce replay protection
- Deterministic normalization:
  - weather -> integer Celsius
  - price -> 2-decimal USD float
  - social -> bounded integer buzz score

## Configuration

SDK:

- `GENLAYER_RELAY_URL`
- `GENLAYER_PUBLIC_KEY_PATH` or `GENLAYER_PUBLIC_KEY_PEM`

Relay:

- `GENLAYER_PRIVATE_KEY_PATH` or `GENLAYER_PRIVATE_KEY_PEM`
- `GENLAYER_WEATHER_PROVIDER` (`mock`, `open-meteo`)
- `GENLAYER_PRICE_PROVIDER` (`mock`, `coingecko`)
- `GENLAYER_SOCIAL_PROVIDER` (`mock`, `reddit`)
- `COINGECKO_API_KEY` (optional)
- `REDDIT_USER_AGENT` (optional)
- `GENLAYER_MAX_SKEW_SECONDS`

## Development

Run tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Contribution targets:

- Add provider implementations behind `relay_service/providers.py`
- Preserve deterministic response shaping across validators
- Maintain signed canonical payload verification in SDK
- Add tests for adapters and failure paths

## Production Notes

- Pin relay public key in SDK for production (avoid dynamic key discovery)
- Keep private keys in secure key management
- Replace in-memory nonce store with Redis/durable storage for scale
- Add key IDs and rotation policy for higher assurance deployments
