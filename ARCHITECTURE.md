# Architecture

## High-Level Flow

1. Intelligent Contract calls SDK function (`get_temperature`, `get_price`, `get_social_buzz`).
2. SDK sends request to relay with:
   - business payload,
   - `nonce`,
   - `request_timestamp`.
3. Relay validates schema, freshness, and replay constraints.
4. Relay fetches from selected provider backend.
5. Relay normalizes output into deterministic schema.
6. Relay canonicalizes payload and signs SHA-256 digest with Ed25519 private key.
7. SDK receives payload + signature, verifies signature against relay public key.
8. SDK returns verified data to contract logic.

## Components

### SDK (`sdk/genlayer_external`)

- `core.py`
  - relay transport
  - nonce/timestamp generation
  - signature verification gate
- `verifier.py`
  - public key loading (env/path or relay endpoint for dev)
  - Ed25519 verification
- `weather.py`, `prices.py`, `social.py`
  - endpoint-specific wrappers
- `exceptions.py`
  - typed SDK error surface

### Relay (`relay_service`)

- `main.py`
  - API endpoints
  - freshness check
  - replay-protection check
  - signing pipeline
- `schemas.py`
  - strict request models (`extra=forbid`)
- `providers.py`
  - provider abstraction and backend implementations
- `generate_keys.py`
  - local Ed25519 key generation utility

## Determinism Strategy

- Canonical JSON (`sort_keys=True`, compact separators)
- Fixed normalization rules:
  - weather temperature -> integer Celsius
  - price value -> 2 decimal float
- Stable response shape per endpoint
- Relay-signed digest over canonical payload

## Security Model

### Trust Boundaries

- Contract/SDK side: untrusted network, verify cryptographic signature.
- Relay side: trusted key-holding boundary for provider/API access.
- Providers: external/untrusted, normalized and signed only after validation.

### Controls

- Private key remains relay-side only.
- Public key can be pinned in SDK via env/path for production.
- Request freshness window (`GENLAYER_MAX_SKEW_SECONDS`).
- Nonce replay prevention (endpoint-scoped).
- Schema rejection for unexpected fields.

## Configuration

### SDK

- `GENLAYER_RELAY_URL`
- `GENLAYER_PUBLIC_KEY_PATH` or `GENLAYER_PUBLIC_KEY_PEM`

### Relay

- `GENLAYER_PRIVATE_KEY_PATH` or `GENLAYER_PRIVATE_KEY_PEM`
- `GENLAYER_WEATHER_PROVIDER` (`mock`, `open-meteo`)
- `GENLAYER_PRICE_PROVIDER` (`mock`, `coingecko`)
- `GENLAYER_SOCIAL_PROVIDER` (`mock`, `reddit`)
- `COINGECKO_API_KEY` (optional)
- `REDDIT_USER_AGENT` (optional)
- `GENLAYER_MAX_SKEW_SECONDS`

## Endpoint Contracts

### `POST /weather`

Request:

- `city: string`
- `nonce: string`
- `request_timestamp: int`

Response (signed):

- `city: string`
- `temperature: int`
- `timestamp: int`
- `signature: base64`

### `POST /price`

Request:

- `symbol: string`
- `nonce: string`
- `request_timestamp: int`

Response (signed):

- `symbol: string`
- `price: float`
- `timestamp: int`
- `signature: base64`

### `POST /social`

Request:

- `platform: string` (currently `reddit`)
- `topic: string`
- `nonce: string`
- `request_timestamp: int`

Response (signed):

- `platform: string`
- `topic: string`
- `buzz_score: int`
- `mentions: int`
- `timestamp: int`
- `signature: base64`

## Operational Notes

- For local development, relay can expose `/public-key`.
- For production, pin trusted public key in SDK and avoid dynamic discovery.
- For scale, replace in-memory nonce map with Redis or durable store.
- For high-assurance deployments, include key IDs and rotation policy.
