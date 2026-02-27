# Contributing

## Local Setup

```bash
pip install -e .
pip install -r relay_service/requirements.txt
```

## Key Material

Generate local relay keys:

```bash
python relay_service/generate_keys.py
```

Set env vars:

```bash
set GENLAYER_PRIVATE_KEY_PATH=relay_private_key.pem
set GENLAYER_PUBLIC_KEY_PATH=relay_public_key.pem
set GENLAYER_WEATHER_PROVIDER=open-meteo
set GENLAYER_PRICE_PROVIDER=coingecko
# optional
set COINGECKO_API_KEY=your_key
```

## Run

```bash
uvicorn relay_service.main:app --reload --port 8000
```

## Test

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Contribution Targets

- Add real provider implementations behind `relay_service/providers.py`
- Keep output deterministic for validator agreement
- Preserve signed canonical payload verification in SDK
- Add tests for new adapters and failure paths
