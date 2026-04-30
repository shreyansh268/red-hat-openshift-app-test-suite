#test- create namespace, verify it exists, delete it at end

import time, pytest
from kubernetes import client, config
from kubernetes.client.rest import ApiException

NAMESPACE = "test-namespace"

@pytest.fixture(scope="module", autouse=True)
def k8s_client():
    try:
        config.load_kube_config()
    except Exception as e:
        print(f"Error loading kube config: {e}")
        raise
    return client.CoreV1Api()

def test_namespace_lifecycle(k8s_client):
    nsbody = client.V1Namespace(metadata=client.V1ObjectMeta(name=NAMESPACE))
    try:
        k8s_client.create_namespace(nsbody)
    except ApiException as e:
        print(f"Error creating namespace: {e}")
        raise

     # Wait for namespace to appear (simple polling)
    for _ in range(20):
        try:
            ns = k8s_client.read_namespace(NAMESPACE)
            assert ns.metadata.name == NAMESPACE
            break
        except ApiException:
            time.sleep(0.5)
    else:
        pytest.fail(f"Namespace {NAMESPACE} did not appear in time")

    # Optional: additional assertions
    assert ns.status.phase in ("Active", "Terminating")

    # Cleanup
    k8s_client.delete_namespace(NAMESPACE, body=client.V1DeleteOptions())