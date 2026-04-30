import json
import os
import pytest

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def seed_data():
    fixtures_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "seed_data.json")
    with open(fixtures_path) as f:
        return json.load(f)


@pytest.fixture(scope="function")
def created_item_ids(http_client, app_url):
    """Track item IDs created during a test and delete them on teardown."""
    ids = []
    yield ids
    for item_id in ids:
        http_client.delete(f"{app_url}/api/v1/items/{item_id}")
