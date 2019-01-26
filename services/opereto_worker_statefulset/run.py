from opereto.helpers.services import ServiceTemplate
from opereto.helpers.kubernetes_api import KubernetesAPI
from opereto.utils.validations import JsonSchemeValidator, validate_dict, default_variable_pattern, default_variable_name_scheme, item_properties_scheme
from opereto.exceptions import OperetoRuntimeError
from opereto.utils.times import get_utc_current_ts


from pyopereto.client import OperetoClient, OperetoClientError
import time


class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        self.client = OperetoClient()
        ServiceTemplate.__init__(self, **kwargs)

    def validate_input(self):

        input_scheme = {
            "type": "object",
            "properties": {
                "deployment_operation": {
                    "enum": ['create', 'modify', 'delete']
                },
                "deployment_name": {
                    "type": "string",
                    "pattern": "^[a-z]{1}[a-z-]{2,125}[a-z]{1}$"
                },
                "worker_image": {
                    "type": "string",
                    "minLength": 1
                },
                "worker_image_memory": {
                    "type": "string",
                    "minLength": 1
                },
                "worker_replicas": {
                    "type": "integer"
                },
                "storage_size": {
                    "type": "string",
                    "minLength": 1
                },
                "storage_class_name": {
                    "type": "string",
                    "minLength": 1
                },
                "agent_java_config": {
                    "type": "string",
                    "minLength": 1
                },
                "agent_log_level": {
                    "enum": ['info', 'warn', 'error', 'fatal','debug']
                },
                "worker_config": {
                    "type": "string",
                    "minLength": 1
                },
                "volumes_mount": {
                    "type": "array"
                },

                "agent_properties": item_properties_scheme,
                "required": ['deployment_operation', 'deployment_name',
                             'worker_image_memory' , 'worker_image', 'worker_replicas', 'storage_size',
                             'storage_class_name', 'agent_java_config', 'agent_log_level', 'worker_config',
                             'volumes_mount', 'agent_properties'],
                "additionalProperties": True
            }
        }

        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()

        if self.input['deployment_name']=='opereto-worker-node':
            raise OperetoRuntimeError(error='Deployment name is invalid, this name is used for Opereto standard workers. Please insert different name.')

        if self.input['worker_replicas']==0:
            raise OperetoRuntimeError(error='There must be at least 1 worker replica specified.')


    def process(self):


        def _get_agent_names():
            names=[]
            for count in range(self.input['worker_replicas']):
                names.append(self.deployment_name+'-'+str(count))
            return names

        def _modify_agent(agent_id):
            try:
                self.client.get_agent(agent_id)
            except OperetoClientError:
                self.client.create_agent(agent_id=agent_id, name=agent_id,
                                         description='This agent worker is part of {} worker stateful set.'.format(
                                             self.deployment_name))
                time.sleep(2)
            agent_properties = self.input['agent_properties']
            agent_properties.update({'opereto.shared': True, 'worker.label': self.deployment_name})
            self.client.modify_agent_properties(agent_id, agent_properties)

        def _agents_status(online=True):
            while (True):
                ok = True
                for agent_id in _get_agent_names():
                    try:
                        agent_attr = self.client.get_agent(agent_id)
                        if agent_attr['online']!=online:
                            ok = False
                            break
                    except OperetoClientError:
                        pass
                if ok:
                    break
                time.sleep(5)


        if self.deployment_operation=='create':
            print 'Creating worker stateful set..'
            resp = self.kubernetes_api.create_stateful_set(self.stateful_set_template)
            for agent_id in _get_agent_names():
                _modify_agent(agent_id)
            print 'Waiting that all worker pods will be online (may take some time)..'
            _agents_status(online=True)
            resp = self.kubernetes_api.get_stateful_set(self.deployment_name)
            print resp.status

        elif self.deployment_operation=='modify':
            print 'Modifying worker stateful set..'
            resp = self.kubernetes_api.modify_stateful_set(self.deployment_name, self.stateful_set_template)
            for agent_id in _get_agent_names():
                _modify_agent(agent_id)
            print 'Waiting that all worker pods will be online (may take some time)..'
            _agents_status(online=True)
            resp = self.kubernetes_api.get_stateful_set(self.deployment_name)
            print resp.status


        elif self.deployment_operation=='delete':
            print 'Deleting worker stateful set..'
            resp = self.kubernetes_api.delete_stateful_set(self.deployment_name)
            print 'Waiting that all worker pods will be offline (may take some time)..'
            _agents_status(online=False)
        return self.client.SUCCESS


    def setup(self):
        self.kubernetes_api = KubernetesAPI()
        self.deployment_name = self.input['deployment_name']
        self.deployment_operation = self.input['deployment_operation']


        self.stateful_set_template = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": self.deployment_name
            },
            "spec": {
                "replicas": self.input['worker_replicas'],
                "selector": {
                    "matchLabels": {
                        "app": self.deployment_name+"-cluster"
                    }
                },
                "updateStrategy": {
                    "type": "RollingUpdate"
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": self.deployment_name+"-cluster",
                            "opereto-pid": "{}".format(self.input['pid'])
                        }
                    },
                    "spec": {
                        "terminationGracePeriodSeconds": 10,
                        "containers": [
                            {
                                "image": self.input['worker_image'],
                                "name": self.deployment_name+"-worker",
                                "resources": {
                                    "requests": {
                                        "memory": self.input['worker_image_memory']
                                    },
                                    "limits": {
                                        "memory": self.input['worker_image_memory']
                                    }
                                },
                                "env": [
                                    {
                                        "name": "agent_name",
                                        "valueFrom": {
                                            "fieldRef": {
                                                "fieldPath": "metadata.name"
                                            }
                                        }
                                    },
                                    {
                                        "name": "opereto_host",
                                        "value": self.input['opereto_host']
                                    },
                                    {
                                        "name": "opereto_user",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": self.input['worker_config'],
                                                "key": "OPERETO_USERNAME"
                                            }
                                        }
                                    },
                                    {
                                        "name": "opereto_password",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": self.input['worker_config'],
                                                "key": "OPERETO_PASSWORD"
                                            }
                                        }
                                    },
                                    {
                                        "name": "javaParams",
                                        "value": self.input['agent_java_config'],
                                    },
                                    {
                                        "name": "log_level",
                                        "value": self.input['agent_log_level']
                                    }
                                ],
                                "volumeMounts": self.input['volumes_mount']
                            }
                        ]
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": "data"
                        },
                        "spec": {
                            "accessModes": [
                                "ReadWriteOnce"
                            ],
                            "storageClassName": self.input['storage_class_name'],
                            "resources": {
                                "requests": {
                                    "storage": self.input['storage_size']
                                }
                            }
                        }
                    }
                ]
            }
        }



    def teardown(self):
        pass



if __name__ == "__main__":
    exit(ServiceRunner().run())
