# GenLayer External Adapter SDK

Deterministic external API adapter for GenLayer Intelligent Contracts.

## Includes

- Python SDK package: `genlayer_external`
- FastAPI relay service
- Provider abstraction for weather/price backends
- Ed25519 signature signing and verification
- Weather and price modules
- Demo intelligent contract
- Replay and freshness protection

## Live Providers

- Weather: `open-meteo` (no key required)
- Price: `coingecko` (optional key via `COINGECKO_API_KEY`)
- Local deterministic fallback: `mock`

## Architecture

Intelligent Contract -> SDK -> Relay -> External API -> Signed Response -> Validator Verification

## Quickstart

1. Install SDK and relay dependencies from repo root:

```bash
pip install -e .
pip install -r relay_service/requirements.txt
```

2. (Optional but recommended) generate a persistent relay keypair:

```bash
python relay_service/generate_keys.py
```

3. Configure environment:

```bash
# copy .env.example values into your shell or .env loader
set GENLAYER_PRIVATE_KEY_PATH=relay_private_key.pem
set GENLAYER_PUBLIC_KEY_PATH=relay_public_key.pem
set GENLAYER_WEATHER_PROVIDER=open-meteo
set GENLAYER_PRICE_PROVIDER=coingecko
# optional
set COINGECKO_API_KEY=your_key
```

4. Start relay from repo root:

```bash
uvicorn relay_service.main:app --reload --port 8000
```

5. Use SDK:

```python
from genlayer_external.weather import get_temperature
from genlayer_external.prices import get_price

print(get_temperature("London"))
print(get_price("ETH"))
```

## Key Configuration

Relay signing key options:

- `GENLAYER_PRIVATE_KEY_PEM`: PEM content in env var
- `GENLAYER_PRIVATE_KEY_PATH`: path to PEM file

SDK verification key options:

- `GENLAYER_PUBLIC_KEY_PEM`: PEM content in env var
- `GENLAYER_PUBLIC_KEY_PATH`: path to PEM file
- If neither is set, SDK fetches `GET /public-key` from relay (development convenience).

## Security Model

- Canonical JSON serialization
- SHA-256 digest signing
- Ed25519 signature verification
- Deterministic response payload fields
- Request freshness validation (`request_timestamp` window)
- Replay protection with endpoint-scoped nonces
- Deterministic normalization of external values (int C, 2-decimal USD)

## Running Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Contribution Scope

This project is designed for GenLayer Builders contributions in Tools and Infrastructure:

- API adapter libraries for Intelligent Contracts
- Relay pattern for private API key and signing boundary
- Deterministic, verifiable responses for validator agreement
- DX improvements through packaging, tests, and local setup defaults

## Production Hardening

- Store private keys in a secure key manager
- Enforce timestamp freshness checks
- Add replay protection nonce
- Add strict request/response schema validation
- Pin relay public key in SDK instead of runtime key discovery
