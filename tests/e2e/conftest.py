import json
import os
import pytest

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def seed_data():
    fixtures_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "seed_data.json")
    with open(fixtures_path) as f:
        return json.load(f)


@pytest.fixture(scope="function")
def cleanup_items(http_client, app_url):
    """Accumulate created item IDs and delete all on teardown."""
    created = []
    yield created
    for item_id in created:
        http_client.delete(f"{app_url}/api/v1/items/{item_id}")
