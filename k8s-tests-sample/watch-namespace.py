from kubernetes import client, config, watch

config.load_kube_config()

v1 = client.CoreV1Api()
w =watch.Watch()
count = 10
for event in w.stream(v1.list_namespace, timeout_seconds=60):
    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    count -= 1
    if count == 0:
        w.stop()
print("Stopped watching namespaces after 10 events.")
