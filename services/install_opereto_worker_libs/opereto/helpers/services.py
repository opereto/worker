from pyopereto.client import OperetoClient, OperetoClientError
from opereto.exceptions import OperetoRuntimeError
import traceback
import abc, sys


class ServiceTemplate(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        self.client = OperetoClient()
        self.input = self.client.input
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

    def _print_error(self, text):
        print >> sys.stderr, text

    def _print_step_title(self, title):
        print('[OPERETO_HTML]<br><font style="color: #222; font-weight: 600; font-size: 13px;">{}</font>'.format(title))

    def _print_notification(self, text):
        print('[OPERETO_HTML]<br><br><font style="width: 800px; padding: 15px; color: #222; font-weight: 400; border:2px solid red; background-color: #f8f8f8;">{}</font><br><br>'.format(text))

    def run(self):
        try:
            self.setup()
            self.validate_input()
            return self.process()
        except OperetoClientError, e:
            print >> sys.stderr, e.message
            print >> sys.stderr, 'Service execution failed.'
            return 1
        except OperetoRuntimeError, e:
            print >> sys.stderr, e.error
            print >> sys.stderr, 'Service execution failed.'
            return 1
        except Exception,e:
            print >> sys.stderr, traceback.format_exc()
            print >> sys.stderr, 'Service execution failed.'
            return 1
        finally:
            self.teardown()



class TaskRunner(ServiceTemplate):

    __metaclass__ = abc.ABCMeta

    def __init__(self, input_scheme={}, **kwargs):
        self.client = OperetoClient()
        self.input_scheme = input_scheme
        ServiceTemplate.__init__(self, **kwargs)


    def validate_input(self):

        default_input_scheme = {
            "type": "object",
            "properties": {
                "debug_mode": {
                    "type": "boolean"
                },
                "pre_task_services": included_services_scheme,

                "valid_exit_codes": {
                    "type": "string"
                },

                "test_parser_config": services_block_scheme,
                "test_results_directory": {
                    "type": ["string", "null"]
                },
                "keep_parser_running": {
                    "type": "integer",
                    "minimum": 5,
                },
                "post_task_services": included_services_scheme,
                "additionalProperties": True
            }
        }

        input_scheme = default_input_scheme.update(self.input_scheme)
        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()

    def _unimplemented_method(self):
        raise Exception, 'Unimplemented method'


    @abc.abstractmethod
    def _running_task(self):
        self._unimplemented_method()

    def process(self):

        if self.input['test_parser_config']:

            if not self.input['test_results_directory']:
                raise Exception('The property value of test_results_directory is missing. ')

            ## run listener
            self._print_step_title('Running test listener..')
            self.listener_pid = self.client.create_process('opereto_test_listener',
                                                           test_results_path=self.listener_results_dir,
                                                           parent_pid=self.parent_pid, debug_mode=self.debug_mode)

            ## run parser
            self._print_step_title('Running test parser: {}..'.format(self.input['test_parser_config']['service']))
            parser_input = self.input['test_parser_config'].get('input') or {}
            parser_input.update({'parser_directory_path': self.host_test_result_directory,
                                 'listener_directory_path': self.listener_results_dir, 'debug_mode': self.debug_mode})
            self.parser_pid = self.client.create_process(self.input['test_parser_config']['service'], **parser_input)

            time.sleep(5)


        ## run tool
        (exc, out, error) = self._running_task()

        if exc not in self.valid_exit_codes:
            print >> sys.stderr, 'Execution failed.'
            self.ok = False

        if self.listener_pid:
            listener_frequency = self.client.get_process_properties(self.listener_pid, 'listener_frequency')
            wait_for_listener = int(listener_frequency)*3
            print 'Waiting for listener to end.. ({} seconds)'.format(wait_for_listener)
            time.sleep(wait_for_listener)  ## wait for listener to stop
            status = self.client.get_process_status(self.listener_pid)
            print 'Listener status is {}'.format(status)
            if status=='in_process':
                print 'Still waiting for listener to end.. ({} seconds)'.format(wait_for_listener)
                time.sleep(wait_for_listener)  ## wait for listener to stop
                status = self.client.get_process_status(self.listener_pid)
            if status == 'in_process':
                print 'Listener still running. Ignoring listener result.'
            if status in ['error', 'failure']:
                print >> sys.stderr, 'Listener indicates on a failure of the test suite..'
                self.ok = False

        if self.ok:
            return self.client.SUCCESS
        return self.client.FAILURE


    def setup(self):
        self.ok = True
        self.parent_pid = self.input['opereto_parent_flow_id'] or self.input['pid']
        self.debug_mode = self.input['debug_mode']
        self.listener_pid = None
        self.parser_pid = None
        self.listener_results_dir = os.path.join(self.input['opereto_workspace'], 'opereto_listener_results')
        self.host_test_result_directory = os.path.join(self.input['opereto_workspace'], 'opereto_parser_results')
        if self.input['test_parser_config']:
            make_directory(self.host_test_result_directory)

        self.valid_exit_codes = [0]
        if self.client.input['valid_exit_codes']:
            codes = self.client.input['valid_exit_codes'].split(',')
            self.valid_exit_codes = []
            for code in codes:
                self.valid_exit_codes.append(int(code))

        ## run pre task services
        for service in self.input['pre_task_services']:
            input = service.get('input') or {}
            agent = service.get('agents') or self.agent_id
            pid = self.client.create_process(service=service['service'], agent=agent, title=service.get('title'),
                                             **input)
            if not self.client.is_success(pid):
                return self.client.FAILURE


    def teardown(self):
        try:
            if self.input['test_parser_config']:
                time.sleep(self.input['keep_parser_running'])

                if self.parser_pid:
                    self.client.stop_process(self.parser_pid)
                if self.listener_pid:
                    self.client.stop_process(self.listener_pid)

                time.sleep(10) ## wait for processes to get terminated
        finally:
            ## run post task services
            for service in self.input['post_task_services']:
                input = service.get('input') or {}
                agent = service.get('agents') or self.agent_id
                pid = self.client.create_process(service=service['service'], agent=agent, title=service.get('title'),
                                                 **input)
                if not self.client.is_success(pid):
                    return self.client.FAILURE

