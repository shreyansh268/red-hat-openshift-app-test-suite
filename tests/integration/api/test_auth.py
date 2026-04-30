import pytest
import requests as req

pytestmark = pytest.mark.integration


class TestAuthentication:
    def test_no_token_returns_401(self, app_url):
        resp = req.get(f"{app_url}/api/v1/items")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, app_url):
        resp = req.get(
            f"{app_url}/api/v1/items",
            headers={"Authorization": "Bearer this-is-not-a-valid-token"},
        )
        assert resp.status_code == 401

    def test_valid_token_returns_200(self, http_client, app_url):
        resp = http_client.get(f"{app_url}/api/v1/items")
        assert resp.status_code == 200

    def test_expired_token_returns_401(self, app_url):
        # Replace with an actual expired token for your environment
        expired = "eyJhbGciOiJSUzI1NiJ9.expired.signature"
        resp = req.get(
            f"{app_url}/api/v1/items",
            headers={"Authorization": f"Bearer {expired}"},
        )
        assert resp.status_code == 401
