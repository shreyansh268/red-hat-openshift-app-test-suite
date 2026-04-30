import pytest
from k8s_helpers import get_oc_route, list_oc_routes

pytestmark = pytest.mark.smoke

ROUTE_NAME = "python-basic"


def test_route_exists(dyn_client, namespace):
    routes = list_oc_routes(dyn_client, namespace)
    names = [r.metadata.name for r in routes.items]
    assert ROUTE_NAME in names, f"Route '{ROUTE_NAME}' not found in {namespace}. Found: {names}"


def test_route_hostname_matches_app_url(dyn_client, namespace, app_url):
    route = get_oc_route(dyn_client, namespace, ROUTE_NAME)
    expected_host = app_url.replace("https://", "").replace("http://", "").split("/")[0]
    assert route.spec.host == expected_host, (
        f"Route host '{route.spec.host}' does not match APP_URL host '{expected_host}'"
    )


def test_route_tls_termination(dyn_client, namespace):
    route = get_oc_route(dyn_client, namespace, ROUTE_NAME)
    assert route.spec.tls is not None, "Route has no TLS config — expected HTTPS termination"
    assert route.spec.tls.termination in ("edge", "reencrypt", "passthrough")
