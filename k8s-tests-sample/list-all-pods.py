from kubernetes import client, config

#config can be set in Configuration class or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
print("Listing pods with their IPs:")
print(v1.list_namespace())
# list_pods = v1.list_namespaced_pod(namespace="szr995-dev", watch=False) 
# for i in list_pods.items:
#     print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
