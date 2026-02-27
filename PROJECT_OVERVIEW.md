# Project Overview: GenLayer External Adapter SDK + Secure Relay

## Summary

This project provides infrastructure for GenLayer Intelligent Contracts to safely consume external data (weather, prices) through a deterministic and validator-verifiable flow.

Core value:

- Contracts never hold external API keys.
- External responses are normalized deterministically.
- Relay responses are signed and verified by SDK clients.
- Replay and stale-request risks are reduced with nonce and timestamp checks.

## Problem

Intelligent Contracts need off-chain data, but direct API calls introduce:

- nondeterministic behavior across validators,
- API key exposure risk,
- weak trust guarantees for returned data.

## Solution

A two-part system:

1. Python SDK (`genlayer_external`) for contract-side calls and signature verification.
2. FastAPI relay service that:
   - fetches external data from provider backends,
   - normalizes payloads into deterministic formats,
   - signs canonical payload digests (Ed25519),
   - enforces freshness and nonce replay protection.

## Why This Fits Builders: Tools & Infrastructure

- Provides reusable adapter libraries for common external data patterns.
- Implements a secure service boundary for private credentials.
- Improves developer UX with packaging, examples, env templates, and tests.
- Gives teams a base framework to add more providers (including social APIs).

## Current Features

- Weather adapter (`open-meteo` and `mock`)
- Price adapter (`coingecko` and `mock`)
- Canonical JSON + SHA-256 + Ed25519 signature model
- Relay public key discovery endpoint for local development
- Production key pinning support through env/path configuration
- Request schema validation
- Replay protection via endpoint-scoped nonce tracking
- Freshness window enforcement via request timestamp
- Local keypair generation utility

## Repository Structure

- `sdk/genlayer_external/` SDK package used by contracts
- `relay_service/` signed relay service and provider implementations
- `demo_contract/` minimal Intelligent Contract example
- `tests/` relay/SDK and provider behavior tests

## Local Quickstart

```bash
pip install -e .
pip install -r relay_service/requirements.txt
python relay_service/generate_keys.py
```

Set environment variables (Windows PowerShell example):

```powershell
$env:GENLAYER_PRIVATE_KEY_PATH="relay_private_key.pem"
$env:GENLAYER_PUBLIC_KEY_PATH="relay_public_key.pem"
$env:GENLAYER_WEATHER_PROVIDER="open-meteo"
$env:GENLAYER_PRICE_PROVIDER="coingecko"
```

Run relay:

```bash
uvicorn relay_service.main:app --reload --port 8000
```

Run tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Next Extensions

- Add social data providers behind the same deterministic schema/signing pipeline.
- Add provider-level retry and circuit-breaker policies.
- Add key rotation metadata and versioned key IDs in responses.
- Add stricter response schema contracts per endpoint version.
