import sys, os, re, time
from opereto.helpers.services import TaskRunner
from opereto.utils.validations import JsonSchemeValidator, validate_dict, default_variable_pattern
from opereto.utils.osutil import make_directory
from opereto.utils.validations import included_services_scheme, services_block_scheme
from opereto.exceptions import *
from pyopereto.client import OperetoClient


class ServiceRunner(TaskRunner):

    def __init__(self, **kwargs):
        TaskRunner.__init__(self, **kwargs)

    def _validate_input(self):
        input_scheme = {
            "type": "object",
            "properties": {
                "task_services": included_services_scheme,
                "worker_config": {
                    "type": 'object'
                }
            },
            "required": ['worker_config', 'task_services'],
            "additionalProperties": True
        }
        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()

        self.worker_agent_id=None
        self.remove_worker = False
        if not self.input['worker_config'].get('agent_id'):
            worker_config_service = services_block_scheme
            worker_config_service['properties']['agent_id_property'] = {
                "type": "string",
                "pattern": default_variable_pattern
            }
            worker_config_service['required'].append('agent_id_property')

            if not self.input['worker_config'].get('setup') or not self.input['worker_config'].get('teardown'):
                raise OperetoRuntimeError(
                    error='Worker configuration is invalid. Either an existing agent name or setup/teardown worker services must be provided. See service documentation for more details.')
            else:
                scheme = {
                    "type": "object",
                    "properties": {
                        "setup": worker_config_service,
                        "teardown": worker_config_service,
                    },
                    "required": ['setup', 'teardown'],
                    "additionalProperties": True
                }
                validator = JsonSchemeValidator(self.input['worker_config'], scheme)
                validator.validate()

        else:
            scheme = {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type" : "string",
                        "pattern": default_variable_pattern
                    },
                    "required": ['agent_id'],
                    "additionalProperties": True
                }
            }
            validator = JsonSchemeValidator(self.input['worker_config'], scheme)
            validator.validate()

            self.worker_agent_id=self.input['worker_config'].get('agent_id')


    def _run_task(self):
        for task_service in self.input['task_services']:
            task_service_input = task_service.get('input') or {}
            pid = self.client.create_process(service=task_service['service'], agent=self.worker_agent_id, title=task_service.get('title'), **task_service_input)
            if not self.client.is_success(pid):
                self.exitcode = self.client.FAILURE


    def _setup(self):
        if not self.input['worker_config'].get('agent_id'):
            service = self.input['worker_config']['setup']
            input = service.get('input') or {}
            agent = service.get('agents') or self.input['opereto_agent']
            pid = self.client.create_process(service=service['service'], agent=agent,
                                             title=service.get('title'), **input)
            if not self.client.is_success(pid):
                raise OperetoRuntimeError('Setup worker failed.')

            self.worker_agent_id = self.client.get_process_property(pid, service['agent_id_property'])
            self.remove_worker = True



    def _teardown(self):
        if self.remove_worker and self.worker_agent_id:
            service = self.input['worker_config']['teardown']
            agent = service.get('agents') or self.input['opereto_agent']
            input = service.get('input') or {}
            input.update({service['agent_id_property']: self.worker_agent_id})
            pid = self.client.create_process(service=service['service'], agent=agent,
                                             title=service.get('title'), **input)
            if not self.client.is_success(pid):
                raise OperetoRuntimeError(error='Teardown worker failed.')


if __name__ == "__main__":
    exit(ServiceRunner().run())
