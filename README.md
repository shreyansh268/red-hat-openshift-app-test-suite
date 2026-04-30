# Red Hat OpenShift App Test Suite

Pytest-based test framework for a Python application deployed on Red Hat OpenShift. Tests run inside Docker containers and are orchestrated via GitHub Actions with `workflow_dispatch`.

**Live app:** https://python-basic-szr995-dev.apps.rm3.7wse.p1.openshiftapps.com/

---

## Structure

```
.github/workflows/test.yml   # GitHub Actions workflow
tests/
  conftest.py                # Shared fixtures: kubernetes client, HTTP session
  k8s_helpers.py             # Kubernetes/OpenShift utility functions
  Dockerfile.test            # Test runner image (python:3.12-slim)
  docker-compose.yml         # Smoke / integration / e2e services

  smoke/                     # Fast gate tests — run first, block other suites on failure
    test_health.py           # Liveness, readiness, replica count, crash loop detection
    test_routes.py           # OpenShift Route exists, hostname, TLS termination

  integration/
    api/test_endpoints.py    # CRUD endpoint tests
    api/test_auth.py         # Auth token validation (401 flows)
    test_k8s_resources.py    # ConfigMap keys, Secrets, resource limits, probes

  e2e/
    test_user_flows.py       # Full item lifecycle + pod deletion resiliency

  fixtures/seed_data.json    # Shared test data
  scripts/wait-for-ready.sh  # Polls /healthz before tests run

k8s-tests-sample/            # Standalone exploratory scripts (not part of the suite)
```

---

## Running via GitHub Actions

1. Go to **Actions → Run Tests → Run workflow**
2. Select:
   - **Environment:** `dev` / `staging` / `prod`
   - **Suite:** `smoke` / `integration` / `e2e` / `all`
   - **Namespace** *(optional)*: defaults to the current OC project

### Required GitHub Secrets (per environment)

| Secret | Description |
|---|---|
| `OC_SERVER` | OpenShift API server URL |
| `OC_TOKEN` | Service account token with view + exec permissions |
| `AUTH_TOKEN` | App-level bearer token for API requests |
| `DB_URL` | Database connection string *(integration only)* |

---

## Running Locally

```bash
# 1. Export required env vars
export APP_URL=https://python-basic-szr995-dev.apps.rm3.7wse.p1.openshiftapps.com
export OC_SERVER=https://<your-cluster-api>:6443
export OC_TOKEN=<your-token>
export OC_NAMESPACE=szr995-dev
export AUTH_TOKEN=<your-app-token>

# 2. Run a suite
cd tests
docker compose run --rm smoke
docker compose run --rm integration
docker compose run --rm e2e

# 3. Or run pytest directly (with a local kubeconfig)
cd tests
pip install -r requirements.txt
pytest smoke/ -m smoke -v
```

---

## Job Pipeline

```
workflow_dispatch
      │
  preflight  (oc login → discover APP_URL → wait-for-ready)
      │
   smoke  ──── fail → pipeline stops
      │
  ┌───┴────┐
  integ    e2e    (parallel)
  └───┬────┘
   report  (always runs — publishes JUnit summary)
```

---

## Key Design Notes

- **No `oc` CLI in test containers** — OpenShift Routes and other CRDs are accessed via the `kubernetes` Python dynamic client (`route.openshift.io/v1`)
- **Auth** is token-based (`OC_TOKEN` + `OC_SERVER` env vars); no kubeconfig file mounting required
- **Cleanup** — integration and e2e fixtures delete created resources on teardown
- **Resiliency test** — `test_cluster_resiliency` deletes a pod and asserts the app stays reachable
