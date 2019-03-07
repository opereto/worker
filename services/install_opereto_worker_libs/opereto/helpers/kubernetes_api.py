from kubernetes import client as kubernetes_client, config as kubernetes_config
import time


class KubernetesAPI(object):

    def __init__(self, namespace='default'):
        self.client = kubernetes_client
        self.namespace = namespace
        kubernetes_config.load_incluster_config()
        self.v1 = kubernetes_client.CoreV1Api()
        self.v1b1 = kubernetes_client.AppsV1beta1Api()
        self.v1b2 = kubernetes_client.AppsV1beta2Api()
        self.v1b1Storage = kubernetes_client.StorageV1beta1Api()
        self.v1b1Extensions = kubernetes_client.ExtensionsV1beta1Api()
        self.AppsV1Api = kubernetes_client.AppsV1Api()
        self.v1_body_delete = kubernetes_client.V1DeleteOptions()
        self.batch_api = kubernetes_client.BatchV1Api()

    def get_pods(self):
        res = self.v1.list_namespaced_pod(self.namespace)
        return [i.metadata.name for i in res.items]


    def run_pod(self, pod_manifest):

        pod_name = pod_manifest['metadata']['name']

        try:
            self.v1.create_namespaced_pod(body=pod_manifest, namespace=self.namespace)

            while True:
                resp = self.v1.read_namespaced_pod(name=pod_name, namespace=self.namespace)
                if resp.status.phase != 'Pending':
                    break
                time.sleep(1)

            for line in self.v1.read_namespaced_pod_log(pod_name, self.namespace, follow=True,
                                                                 _preload_content=False).stream():
                print(line)
        finally:
            resp = self.v1.delete_namespaced_pod(
                name=pod_name, namespace=self.namespace,
                body={})


    def create_stateful_set(self, deployment_manifest):
        resp = self.AppsV1Api.create_namespaced_stateful_set(
            body=deployment_manifest, namespace=self.namespace)
        return resp

    def modify_stateful_set(self, name, deployment_manifest):
        resp = self.AppsV1Api.patch_namespaced_stateful_set(
            name=name, body=deployment_manifest, namespace=self.namespace)
        return resp

    def delete_stateful_set(self, name):
        resp = self.AppsV1Api.delete_namespaced_stateful_set(name=name, namespace=self.namespace, body={}, grace_period_seconds=0)
        return resp

    def get_stateful_set(self, name):
        resp = self.AppsV1Api.read_namespaced_stateful_set(name=name, namespace=self.namespace)
        return resp


