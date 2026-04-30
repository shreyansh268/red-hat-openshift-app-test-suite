import pytest
from k8s_helpers import wait_for_deployment, assert_pods_running

pytestmark = pytest.mark.smoke

APP_NAME = "python-basic"     # update to match your Deployment/DeploymentConfig name
APP_LABEL = "app=python-basic"


def test_liveness_endpoint(http_client, app_url):
    resp = http_client.get(f"{app_url}/")
    assert resp.status_code == 200


def test_readiness_endpoint(http_client, app_url):
    resp = http_client.get(f"{app_url}/")
    assert resp.status_code == 200


def test_deployment_all_replicas_available(apps_v1, namespace):
    deploy = apps_v1.read_namespaced_deployment(APP_NAME, namespace)
    desired = deploy.spec.replicas or 0
    available = deploy.status.available_replicas or 0
    assert available == desired, (
        f"Expected {desired} replicas available, got {available}"
    )


def test_pods_running(core_v1, namespace):
    assert_pods_running(core_v1, namespace, APP_LABEL)


def test_no_crashlooping_pods(core_v1, namespace):
    pods = core_v1.list_namespaced_pod(namespace, label_selector=APP_LABEL)
    crashlooping = [
        p.metadata.name
        for p in pods.items
        for cs in (p.status.container_statuses or [])
        if cs.state.waiting and cs.state.waiting.reason in (
            "CrashLoopBackOff", "OOMKilled", "Error"
        )
    ]
    assert not crashlooping, f"Pods in crash loop: {crashlooping}"
