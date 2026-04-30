import os
import pytest
import requests
from kubernetes import client, config, dynamic
from kubernetes.client import api_client as k8s_api_client


def _configure_k8s():
    """Configure kubernetes client from env vars or kubeconfig."""
    oc_server = os.environ.get("OC_SERVER")
    oc_token = os.environ.get("OC_TOKEN")
    kubeconfig = os.environ.get("KUBECONFIG")

    if kubeconfig:
        config.load_kube_config(config_file=kubeconfig)
    elif oc_server and oc_token:
        # Token-based auth: used in CI where oc login ran in the workflow job
        # but the token is passed directly to avoid kubeconfig file mounting
        configuration = client.Configuration()
        configuration.host = oc_server
        configuration.api_key = {"authorization": f"Bearer {oc_token}"}
        configuration.verify_ssl = False
        client.Configuration.set_default(configuration)
    else:
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()


# ── Kubernetes / OpenShift fixtures ──────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def k8s_setup():
    _configure_k8s()


@pytest.fixture(scope="session")
def namespace():
    return os.environ.get("OC_NAMESPACE", "default")


@pytest.fixture(scope="session")
def core_v1(k8s_setup):
    return client.CoreV1Api()


@pytest.fixture(scope="session")
def apps_v1(k8s_setup):
    return client.AppsV1Api()


@pytest.fixture(scope="session")
def dyn_client(k8s_setup):
    """Dynamic client for OpenShift-specific CRDs (Routes, DeploymentConfigs, etc.)"""
    return dynamic.DynamicClient(k8s_api_client.ApiClient())


# ── HTTP client fixtures ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app_url():
    url = os.environ.get("APP_URL", "").rstrip("/")
    assert url, "APP_URL environment variable is required"
    return url


@pytest.fixture(scope="session")
def auth_headers():
    token = os.environ.get("AUTH_TOKEN", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


@pytest.fixture(scope="session")
def http_client(app_url, auth_headers):
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    session.headers.update(auth_headers)
    return session
