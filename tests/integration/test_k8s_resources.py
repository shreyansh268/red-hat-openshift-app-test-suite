"""
Integration tests that verify cluster-side state matches application expectations.
Uses the kubernetes Python client directly — no oc CLI required.
"""
import pytest
from k8s_helpers import get_configmap_value, wait_for_deployment

pytestmark = pytest.mark.integration

APP_NAME = "python-basic"
APP_LABEL = "app=python-basic"


def test_app_configmap_has_required_keys(core_v1, namespace):
    cm = core_v1.read_namespaced_config_map("my-app-config", namespace)
    required_keys = {"APP_ENV", "LOG_LEVEL"}
    missing = required_keys - set(cm.data.keys())
    assert not missing, f"ConfigMap missing keys: {missing}"


def test_app_secret_exists(core_v1, namespace):
    secret = core_v1.read_namespaced_secret("my-app-secret", namespace)
    assert secret is not None
    assert "DATABASE_URL" in secret.data


def test_deployment_has_resource_limits(apps_v1, namespace):
    deploy = apps_v1.read_namespaced_deployment(APP_NAME, namespace)
    for container in deploy.spec.template.spec.containers:
        assert container.resources.limits, (
            f"Container '{container.name}' has no resource limits set"
        )
        assert "memory" in container.resources.limits
        assert "cpu" in container.resources.limits


def test_deployment_has_liveness_probe(apps_v1, namespace):
    deploy = apps_v1.read_namespaced_deployment(APP_NAME, namespace)
    for container in deploy.spec.template.spec.containers:
        assert container.liveness_probe is not None, (
            f"Container '{container.name}' has no liveness probe"
        )


def test_deployment_has_readiness_probe(apps_v1, namespace):
    deploy = apps_v1.read_namespaced_deployment(APP_NAME, namespace)
    for container in deploy.spec.template.spec.containers:
        assert container.readiness_probe is not None, (
            f"Container '{container.name}' has no readiness probe"
        )


def test_service_exists_and_has_correct_port(core_v1, namespace):
    svc = core_v1.read_namespaced_service(APP_NAME, namespace)
    port_numbers = [p.port for p in svc.spec.ports]
    assert 8080 in port_numbers, f"Expected port 8080, found: {port_numbers}"
