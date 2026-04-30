from kubernetes import client, config
from kubernetes.client.rest import ApiException

#config can be set in Configuration class or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()

try:
    ns = v1.read_namespace("szr995-dev")
    print("You can access namespace:", ns.metadata.name)
except ApiException as e:
    print("Status:", e.status, "Body:", e.body)



# List all projects (namespaces)
#cannot do because of access rights
# namespaces = v1.list_namespace()
# for ns in namespaces.items:
#     print(ns.metadata.name)

# pods = v1.list_namespaced_pod("szr995-dev")
# for p in pods.items:
#     print(p.metadata.name)