import kopf
import kubernetes.client
from kubernetes.client.rest import ApiException

def create_nginx_deployment(name, replicas, namespace):
    api = kubernetes.client.AppsV1Api()
    deployment = kubernetes.client.V1Deployment(
        metadata=kubernetes.client.V1ObjectMeta(name=name, namespace=namespace),
        spec=kubernetes.client.V1DeploymentSpec(
            replicas=replicas,
            selector={"matchLabels": {"app": name}},
            template=kubernetes.client.V1PodTemplateSpec(
                metadata={"labels": {"app": name}},
                spec=kubernetes.client.V1PodSpec(
                    containers=[
                        kubernetes.client.V1Container(
                            name="nginx",
                            image="nginx:latest",
                            ports=[kubernetes.client.V1ContainerPort(container_port=80)],
                        )
                    ]
                ),
            ),
        ),
    )
    try:
        api.create_namespaced_deployment(namespace=namespace, body=deployment)
        print(f"✅ Deployment {name} created in namespace {namespace}.")
    except ApiException as e:
        print(f"⚠️ Failed to create Deployment: {e}")

def create_nginx_service(name, node_port, namespace):
    api = kubernetes.client.CoreV1Api()
    service = kubernetes.client.V1Service(
        metadata=kubernetes.client.V1ObjectMeta(name=name, namespace=namespace),
        spec=kubernetes.client.V1ServiceSpec(
            selector={"app": name},
            ports=[
                kubernetes.client.V1ServicePort(
                    port=80, target_port=80, node_port=node_port
                )
            ],
            type="NodePort",
        ),
    )
    try:
        api.create_namespaced_service(namespace=namespace, body=service)
        print(f"✅ Service {name} created in namespace {namespace} with NodePort {node_port}.")
    except ApiException as e:
        print(f"⚠️ Failed to create Service: {e}")

@kopf.on.create("example.com", "v1", "nginxes")
def create_nginx_handler(spec, name, namespace, **kwargs):
    replicas = spec.get("replicas", 1)
    node_port = spec.get("nodePort", 38888)
    create_nginx_deployment(name, replicas, namespace)
    create_nginx_service(name, node_port, namespace)

