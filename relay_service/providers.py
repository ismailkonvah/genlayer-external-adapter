import os
from typing import Protocol

import requests


class WeatherProvider(Protocol):
    def get_temperature(self, city: str) -> int:
        ...


class PriceProvider(Protocol):
    def get_price(self, symbol: str) -> float:
        ...


class MockWeatherProvider:
    def get_temperature(self, city: str) -> int:
        # Stable deterministic output for local development/testing.
        return 25


class MockPriceProvider:
    def get_price(self, symbol: str) -> float:
        # Stable deterministic output for local development/testing.
        return 3000.0


class OpenMeteoWeatherProvider:
    def __init__(self, timeout_seconds: int = 10):
        self.timeout_seconds = timeout_seconds

    def _geocode(self, city: str) -> tuple[float, float]:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results") or []
        if not results:
            raise ValueError(f"City not found: {city}")
        first = results[0]
        return float(first["latitude"]), float(first["longitude"])

    def get_temperature(self, city: str) -> int:
        lat, lon = self._geocode(city)
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "current": "temperature_2m"},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        current = payload.get("current") or {}
        temperature = current.get("temperature_2m")
        if temperature is None:
            raise ValueError("Open-Meteo missing current.temperature_2m")
        # Deterministic normalization: integer Celsius.
        return int(round(float(temperature)))


class CoinGeckoPriceProvider:
    def __init__(self, timeout_seconds: int = 10):
        self.timeout_seconds = timeout_seconds
        self.api_key = os.getenv("COINGECKO_API_KEY")

    def _symbol_to_id(self, symbol: str) -> str:
        mapping = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "USDC": "usd-coin",
            "USDT": "tether",
        }
        upper = symbol.upper()
        return mapping.get(upper, upper.lower())

    def get_price(self, symbol: str) -> float:
        coin_id = self._symbol_to_id(symbol)
        headers = {}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key

        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"},
            headers=headers,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        usd = (payload.get(coin_id) or {}).get("usd")
        if usd is None:
            raise ValueError(f"CoinGecko missing usd price for symbol: {symbol}")
        # Deterministic normalization: fixed 2 decimals.
        return round(float(usd), 2)


def load_weather_provider() -> WeatherProvider:
    provider_name = os.getenv("GENLAYER_WEATHER_PROVIDER", "mock").lower()
    if provider_name == "mock":
        return MockWeatherProvider()
    if provider_name == "open-meteo":
        return OpenMeteoWeatherProvider()
    raise ValueError(f"Unsupported weather provider: {provider_name}")


def load_price_provider() -> PriceProvider:
    provider_name = os.getenv("GENLAYER_PRICE_PROVIDER", "mock").lower()
    if provider_name == "mock":
        return MockPriceProvider()
    if provider_name == "coingecko":
        return CoinGeckoPriceProvider()
    raise ValueError(f"Unsupported price provider: {provider_name}")
