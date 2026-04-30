import pytest

pytestmark = pytest.mark.e2e


class TestItemLifecycle:
    def test_full_crud_flow(self, http_client, app_url, seed_data, cleanup_items):
        # Create
        resp = http_client.post(f"{app_url}/api/v1/items", json=seed_data["item"])
        assert resp.status_code == 201
        item_id = resp.json()["id"]
        cleanup_items.append(item_id)

        # Verify appears in list
        list_resp = http_client.get(f"{app_url}/api/v1/items")
        ids = [i["id"] for i in list_resp.json()]
        assert item_id in ids

        # Update
        patch_resp = http_client.patch(
            f"{app_url}/api/v1/items/{item_id}", json={"name": "e2e-updated"}
        )
        assert patch_resp.status_code == 200

        # Read back and confirm update
        get_resp = http_client.get(f"{app_url}/api/v1/items/{item_id}")
        assert get_resp.json()["name"] == "e2e-updated"

        # Delete
        del_resp = http_client.delete(f"{app_url}/api/v1/items/{item_id}")
        assert del_resp.status_code in (200, 204)
        cleanup_items.remove(item_id)

        # Confirm gone
        gone_resp = http_client.get(f"{app_url}/api/v1/items/{item_id}")
        assert gone_resp.status_code == 404


class TestClusterResiliency:
    def test_app_recovers_after_pod_deletion(self, core_v1, apps_v1, namespace,
                                              http_client, app_url):
        """Delete one pod and verify the app stays reachable (k8s restarts it)."""
        from k8s_helpers import wait_for_deployment
        import time

        pods = core_v1.list_namespaced_pod(namespace, label_selector="app=python-basic")
        assert pods.items, "No pods found to delete"

        target_pod = pods.items[0].metadata.name
        core_v1.delete_namespaced_pod(target_pod, namespace)

        # Brief wait for k8s to notice and start replacement
        time.sleep(5)

        # App should still respond during pod restart (assuming >1 replica)
        resp = http_client.get(f"{app_url}/healthz")
        assert resp.status_code == 200

        # Wait for full rollout to stabilise
        wait_for_deployment(apps_v1, "python-basic", namespace, timeout=120)
