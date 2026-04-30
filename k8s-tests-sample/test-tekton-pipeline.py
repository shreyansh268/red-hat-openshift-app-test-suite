from kubernetes import client, config
import time, pytest

config.load_kube_config()
custom_api = client.CustomObjectsApi()

def test_tekton_pipeline_success():
    status, reason = wait_for_pipeline_run("szr995-dev", "hello-world-pipeline")
    #assert full trajectory of pipeline run is successful
    assert status == "True", f"pipeline failed reason: {reason}"

def test_scan_task_run_before_task_deploy():
    pr= custom_api.get_namespaced_custom_object(group="tekton.dev", version="v1beta1", namespace="szr995-dev", plural="pipelineruns", name="hello-world-pipeline-run")
    task_names=[
        t["pipelineTaskName"]
        for t in pr["status"]["taskRuns"].values()
    ]
    scan_idx=task_names.index("scan")
    deploy_idx=task_names.index("deploy")
    #trajectory assertion
    assert scan_idx < deploy_idx, "scan task should run before deploy task"
