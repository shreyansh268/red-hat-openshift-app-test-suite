import pytest

pytestmark = pytest.mark.integration


class TestItemsCRUD:
    def test_list_returns_200(self, http_client, app_url):
        resp = http_client.get(f"{app_url}/api/v1/items")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_item(self, http_client, app_url, seed_data, created_item_ids):
        resp = http_client.post(f"{app_url}/api/v1/items", json=seed_data["item"])
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        created_item_ids.append(body["id"])

    def test_get_item_by_id(self, http_client, app_url, seed_data, created_item_ids):
        create = http_client.post(f"{app_url}/api/v1/items", json=seed_data["item"])
        item_id = create.json()["id"]
        created_item_ids.append(item_id)

        resp = http_client.get(f"{app_url}/api/v1/items/{item_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == item_id

    def test_get_nonexistent_item_returns_404(self, http_client, app_url):
        resp = http_client.get(f"{app_url}/api/v1/items/nonexistent-id-00000")
        assert resp.status_code == 404

    def test_update_item(self, http_client, app_url, seed_data, created_item_ids):
        create = http_client.post(f"{app_url}/api/v1/items", json=seed_data["item"])
        item_id = create.json()["id"]
        created_item_ids.append(item_id)

        resp = http_client.patch(
            f"{app_url}/api/v1/items/{item_id}", json={"name": "updated-name"}
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "updated-name"

    def test_delete_item(self, http_client, app_url, seed_data):
        create = http_client.post(f"{app_url}/api/v1/items", json=seed_data["item"])
        item_id = create.json()["id"]

        resp = http_client.delete(f"{app_url}/api/v1/items/{item_id}")
        assert resp.status_code in (200, 204)

        # confirm deleted
        get = http_client.get(f"{app_url}/api/v1/items/{item_id}")
        assert get.status_code == 404
