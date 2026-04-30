import time
from kubernetes import client


def wait_for_deployment(apps_v1: client.AppsV1Api, name: str, namespace: str, timeout: int = 120):
    """Poll until all replicas in a deployment are available."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        deploy = apps_v1.read_namespaced_deployment(name, namespace)
        desired = deploy.spec.replicas or 0
        available = deploy.status.available_replicas or 0
        if desired > 0 and available == desired:
            return deploy
        time.sleep(5)
    raise TimeoutError(f"Deployment {name}/{namespace} not ready after {timeout}s")


def get_pod_logs(core_v1: client.CoreV1Api, namespace: str, label_selector: str,
                 container: str = None, tail_lines: int = 50) -> str:
    """Fetch logs from the first pod matching label_selector."""
    pods = core_v1.list_namespaced_pod(namespace, label_selector=label_selector)
    if not pods.items:
        return ""
    pod_name = pods.items[0].metadata.name
    return core_v1.read_namespaced_pod_log(
        pod_name, namespace, container=container, tail_lines=tail_lines
    )


def assert_pods_running(core_v1: client.CoreV1Api, namespace: str, label_selector: str):
    """Assert all pods matching selector are in Running phase."""
    pods = core_v1.list_namespaced_pod(namespace, label_selector=label_selector)
    assert pods.items, f"No pods found for selector '{label_selector}' in {namespace}"
    not_running = [
        p.metadata.name for p in pods.items if p.status.phase != "Running"
    ]
    assert not not_running, f"Pods not Running: {not_running}"


def get_configmap_value(core_v1: client.CoreV1Api, namespace: str, name: str, key: str) -> str:
    cm = core_v1.read_namespaced_config_map(name, namespace)
    return cm.data[key]


def get_oc_route(dyn_client, namespace: str, name: str):
    """Fetch an OpenShift Route resource via the dynamic client."""
    routes_api = dyn_client.resources.get(
        api_version="route.openshift.io/v1", kind="Route"
    )
    return routes_api.get(name=name, namespace=namespace)


def list_oc_routes(dyn_client, namespace: str):
    """List all OpenShift Routes in a namespace."""
    routes_api = dyn_client.resources.get(
        api_version="route.openshift.io/v1", kind="Route"
    )
    return routes_api.get(namespace=namespace)
