import sys
import os
import re
import time
import abc
import traceback
from pyopereto.client import OperetoClient, OperetoClientError
from opereto.utils.validations import included_services_scheme, services_block_scheme, JsonSchemeValidator, validate_dict, default_variable_pattern
from opereto.utils.osutil import make_directory
from opereto.exceptions import *


class ServiceTemplate(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        self.client = OperetoClient()
        self.input = self.client.input
        self.state_file = os.path.join(self.input['opereto_workspace'], '_opereto_service_state.json')
        self.exitcode = 0
        if kwargs:
            self.input.update(kwargs)

    def _unimplemented_method(self):
        raise Exception, 'Unimplemented method'

    @abc.abstractmethod
    def setup(self):
        self._unimplemented_method()

    @abc.abstractmethod
    def process(self):
        self._unimplemented_method()

    @abc.abstractmethod
    def teardown(self):
        self._unimplemented_method()

    @abc.abstractmethod
    def validate_input(self):
        pass


    def _save_state(self, state):
        with open(self.state_file, 'w') as _state_file:
            _state_file.write(json.dumps(state, indent=4))

    def _get_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as _state_file:
                return json.loads(_state_file.read())


    ## temp, due to bug in agent
    def _replace_empty_dict_with_none(self, properties=[]):
        for property in properties:
            if not self.input.get(property):
                self.input[property]=None


    def _print_error(self, text):
        print >> sys.stderr, text

    def _print_step_title(self, title):
        print('[OPERETO_HTML]<br><font style="color: #222; font-weight: 600; font-size: 13px;">{}</font>'.format(title))

    def _print_notification(self, text):
        print('[OPERETO_HTML]<br><br><font style="width: 800px; padding: 15px; color: #222; font-weight: 400; border:2px solid red; background-color: #f8f8f8;">{}</font><br><br>'.format(text))

    def run(self):
        try:
            self.validate_input()
            self.setup()
            self.exitcode = self.process()
        except OperetoClientError, e:
            print >> sys.stderr, e.message
            print >> sys.stderr, 'Service execution failed.'
            self.exitcode = 2
        except OperetoRuntimeError, e:
            print >> sys.stderr, e.error
            print >> sys.stderr, 'Service execution failed.'
            self.exitcode = 2
        except Exception,e:
            print >> sys.stderr, traceback.format_exc()
            print >> sys.stderr, 'Service execution failed : {}'.format(str(e))
            self.exitcode = 1
        finally:
            exc = self.teardown()
            if exc is not None:
                self.exitcode=exc
            return self.exitcode



class TaskRunner(ServiceTemplate):

    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        ServiceTemplate.__init__(self, **kwargs)


    @abc.abstractmethod
    def _setup(self):
        self._unimplemented_method()

    @abc.abstractmethod
    def _teardown(self):
        self._unimplemented_method()

    @abc.abstractmethod
    def _validate_input(self):
        self._unimplemented_method()

    @abc.abstractmethod
    def _run_task(self):
        self._unimplemented_method()


    def validate_input(self):

        self._replace_empty_dict_with_none(['task_service','test_parser_config'])

        input_scheme = {
            "type": "object",
            "properties": {
                "debug_mode": {
                    "type": "boolean"
                },
                "pre_task_services": included_services_scheme,
                "test_parser_config": services_block_scheme,
                "test_results_directory": {
                    "type": ["string", "null"]
                },
                "keep_parser_running": {
                    "type": "integer",
                    "minimum": 5
                },
                "post_task_services": included_services_scheme
            },
            "required": [],
            "additionalProperties": True
        }


        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()
        self._validate_input()

    def process(self):
        try:
            self._run_parser()
            self.task_exitcode = self._run_task()
            self._wait_listener()
        finally:
            return self.task_exitcode

    def _run_service_set(self, service_list):
        for service in service_list:
            input = service.get('input') or {}
            agent = service.get('agents') or self.input['opereto_agent']
            pid = self.client.create_process(service=service['service'], agent=agent, title=service.get('title'),**input)
            if not self.client.is_success(pid):
                raise OperetoRuntimeError(error='Run services set failed')

    def _run_parser(self, agent=None):
        if self.input['test_parser_config']:

            agent = agent or self.input['opereto_agent']
            ## run listener
            self._print_step_title('Running test listener..')
            self.listener_pid = self.client.create_process('opereto_test_listener', test_results_path=self.listener_results_dir, parent_pid=self.parent_pid, debug_mode=self.debug_mode, timeout=self.input['opereto_timeout'], agent=agent)

            ## run parser
            self._print_step_title('Running test parser: {}..'.format(self.input['test_parser_config']['service']))
            parser_input = self.input['test_parser_config'].get('input') or {}
            parser_input.update({'parser_directory_path':self.parser_results_directory, 'listener_directory_path': self.listener_results_dir, 'debug_mode': self.debug_mode})
            self.parser_pid = self.client.create_process(self.input['test_parser_config']['service'], timeout=self.input['opereto_timeout'], agent=agent, **parser_input)
            time.sleep(5)

    def _wait_listener(self, agent=None):
        if self.listener_pid:
            try:
                wait_for_listener = self.input['keep_parser_running']
                print 'Waiting for listener process to collect final results.. ({} seconds)'.format(wait_for_listener)
                time.sleep(wait_for_listener)
            finally:
                self.client.modify_process_property('stop_listener_code', True, pid=self.listener_pid)
                self.client.wait_to_end([self.listener_pid])

    def setup(self):
        self.task_exitcode = 3
        self.task_output = {}
        self.parent_pid = self.input['opereto_parent_flow_id'] or self.input['pid']
        self.debug_mode = self.input['debug_mode']
        self.listener_pid = None
        self.parser_pid = None
        self.listener_results_dir = os.path.join(self.input['opereto_workspace'], 'opereto_listener_results')
        self.parser_results_directory = os.path.join(self.input['opereto_workspace'], 'opereto_parser_results')
        self.test_results_directory = self.input['test_results_directory']
        make_directory(self.parser_results_directory)
        self.task_output_json = os.path.join(self.input['opereto_workspace'], 'opereto_task_output.json')
        make_directory(self.listener_results_dir)
        self._setup()
        self._run_service_set(self.input['pre_task_services'])


    def teardown(self):
        try:
            if self.input['test_parser_config']:
                if self.listener_pid:
                    status = self.client.get_process_status(self.listener_pid)
                    if status in ['error', 'failure']:
                        print >> sys.stderr, 'Listener indicates on a failure of the test suite.'
                        self.task_exitcode = 2

                if self.parser_pid:
                    try:
                        self.client.stop_process(self.parser_pid)
                        self.client.wait_to_end([self.parser_pid])
                    except Exception as e:
                        print >> sys.stderr, str(e)

            exc = self._teardown()
            if exc is not None:
                self.task_exitcode=exc

            self.client.modify_process_property('task_exitcode', self.task_exitcode)
            if os.path.exists(self.task_output_json):
                try:
                    with open(self.task_output_json, 'r') as out_file:
                        output_data = json.loads(out_file.read())
                        self.client.modify_process_property('task_output', output_data)
                except Exception as e:
                    print('Failed to parse task output json file: {}'.format(e))
        finally:
            self._run_service_set(self.input['post_task_services'])
            return(self.task_exitcode)