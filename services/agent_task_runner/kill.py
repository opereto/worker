import sys, os
from opereto.helpers.services import ServiceTemplate
from opereto.utils.misc import status_to_exitcode
from opereto.exceptions import *
from pyopereto.client import OperetoClient


class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        ServiceTemplate.__init__(self, **kwargs)

    def validate_input(self):
        pass

    def setup(self):
        pass

    def teardown(self):
        pass

    def process(self):

        try:
            final_status=0
            if not self.input['worker_config'].get('agent_id'):
                setup_service = self.input['worker_config']['setup']
                teardown_service = self.input['worker_config']['teardown']
                child_processes = self.client.get_process_flow()[0].get('children')
                final_status = status_to_exitcode(self.client.get_process_flow()[0]['exec_status']) or 1
                if child_processes:
                    first_child = child_processes[0]
                    if first_child['service_id']==setup_service['service'] and first_child['exec_status']=='success':
                        last_child = child_processes[-1]
                        if last_child['service_id']==teardown_service['service'] and last_child['exec_status']=='success':
                            pass
                        else:
                            worker_agent_id = self.client.get_process_property(first_child['id'], setup_service['agent_id_property'])
                            if worker_agent_id:
                                agent = teardown_service.get('agents') or self.input['opereto_agent']
                                input = teardown_service.get('input') or {}
                                input.update({teardown_service['agent_id_property']: worker_agent_id})
                                pid = self.client.create_process(service=teardown_service['service'], agent=agent, title=teardown_service.get('title'), **input)
                                if not self.client.is_success(pid):
                                   print >> sys.stderr, 'Please make sure that no worker is yet up and running'
        finally:
            return(final_status)

if __name__ == "__main__":
    exit(ServiceRunner().run())
