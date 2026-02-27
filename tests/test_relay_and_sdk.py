import importlib
import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "sdk"))


class RelaySdkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["GENLAYER_MAX_SKEW_SECONDS"] = "300"
        cls.relay_main = importlib.import_module("relay_service.main")
        cls.client = TestClient(cls.relay_main.app)

    def setUp(self):
        self.relay_main._used_nonces.clear()

    def test_public_key_endpoint(self):
        res = self.client.get("/public-key")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn("public_key_pem", body)
        self.assertIn("BEGIN PUBLIC KEY", body["public_key_pem"])

    def test_replay_protection(self):
        payload = {
            "city": "London",
            "nonce": "nonce-replay-123",
            "request_timestamp": int(time.time()),
        }
        first = self.client.post("/weather", json=payload)
        second = self.client.post("/weather", json=payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)

    def test_timestamp_freshness(self):
        payload = {
            "city": "London",
            "nonce": "nonce-old-123",
            "request_timestamp": int(time.time()) - 10_000,
        }
        res = self.client.post("/weather", json=payload)
        self.assertEqual(res.status_code, 400)

    def test_sdk_signature_verification_flow(self):
        import genlayer_external.core as core
        import genlayer_external.verifier as verifier

        verifier.reset_public_key_cache()
        core.RELAY_URL = "http://relay.test"

        def fake_post(url, *args, **kwargs):
            path = url.replace(core.RELAY_URL, "")
            return self.client.post(path, json=kwargs.get("json"))

        def fake_get(url, *args, **kwargs):
            path = url.replace(core.RELAY_URL, "")
            return self.client.get(path)

        with patch("genlayer_external.core.requests.post", side_effect=fake_post):
            with patch("genlayer_external.verifier.requests.get", side_effect=fake_get):
                data = core.relay_call("weather", {"city": "London"})
                self.assertEqual(data["city"], "London")
                self.assertEqual(data["temperature"], 25)


if __name__ == "__main__":
    unittest.main()
