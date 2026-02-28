import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from relay_service.providers import CoinGeckoPriceProvider, OpenMeteoWeatherProvider, RedditSocialProvider


class ProviderTests(unittest.TestCase):
    def test_open_meteo_temperature_is_normalized_to_int(self):
        geocode_response = Mock()
        geocode_response.raise_for_status.return_value = None
        geocode_response.json.return_value = {"results": [{"latitude": 51.5, "longitude": -0.1}]}

        weather_response = Mock()
        weather_response.raise_for_status.return_value = None
        weather_response.json.return_value = {"current": {"temperature_2m": 24.6}}

        with patch("relay_service.providers.requests.get", side_effect=[geocode_response, weather_response]):
            provider = OpenMeteoWeatherProvider()
            temp = provider.get_temperature("London")
            self.assertEqual(temp, 25)

    def test_coingecko_price_is_normalized_to_2_decimals(self):
        price_response = Mock()
        price_response.raise_for_status.return_value = None
        price_response.json.return_value = {"ethereum": {"usd": 3123.4567}}

        with patch("relay_service.providers.requests.get", return_value=price_response):
            provider = CoinGeckoPriceProvider()
            value = provider.get_price("ETH")
            self.assertEqual(value, 3123.46)

    def test_reddit_buzz_is_deterministically_normalized(self):
        reddit_response = Mock()
        reddit_response.raise_for_status.return_value = None
        reddit_response.json.return_value = {
            "data": {
                "children": [
                    {"data": {"score": 80, "num_comments": 10}},
                    {"data": {"score": 20, "num_comments": 5}},
                ]
            }
        }

        with patch("relay_service.providers.requests.get", return_value=reddit_response):
            provider = RedditSocialProvider()
            buzz_score, mentions = provider.get_buzz("genlayer")
            self.assertEqual(buzz_score, 13)
            self.assertEqual(mentions, 2)


if __name__ == "__main__":
    unittest.main()
