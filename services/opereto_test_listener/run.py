from opereto.helpers.services import ServiceTemplate
from opereto.utils.validations import JsonSchemeValidator, default_entity_name_scheme, process_result_keys, process_status_keys
from opereto.utils.osutil import get_file_md5sum, remove_directory_if_exists, make_directory
from opereto.exceptions import raise_runtime_error
from opereto.settings import MAX_LOG_LINES_PER_PROCESS
from pyopereto.client import OperetoClient
import os, time, json


class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        self.client = OperetoClient()
        ServiceTemplate.__init__(self, **kwargs)
        self._print_step_title('Start opereto test listener..')
        self.sflow_id = self.input['opereto_source_flow_id']

    def validate_input(self):

        input_scheme = {
            "type": "object",
            "properties" : {
                "test_results_path": {
                    "type" : "string",
                    "minLength": 1
                },
                "parent_pid": {
                    "type": "string"
                },
                "listener_frequency": {
                    "type": "integer",
                    "minValue": 1
                },
                "debug_mode": {
                    "type": "boolean"
                }
            },
            "required": ['listener_frequency', 'test_results_path'],
            "additionalProperties": True
        }

        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()

        self.parent_pid = self.input['parent_pid'] or self.input['pid']
        self.test_results_dir = self.input['test_results_path']
        self.debug_mode = self.input['debug_mode']
        self.next_check_source_alive=0

        if not os.path.exists(self.test_results_dir):
            raise_runtime_error('Test results directory {} does not exist.'.format(self.test_results_dir))

        self.result_keys = process_result_keys
        self.status_keys = process_status_keys

        self.tests_json_scheme = {
            "type": "object",
            "properties": {
                "test_suite": {
                    "type": "object",
                    "properties": {
                        "links": {
                            "type": "array"
                        },
                        "status": {
                            "enum": self.status_keys
                        }
                    }
                },
                "test_records": {
                    "type": "array",
                    "items": [
                        {
                            "type": "object",
                            "properties": {
                                "testname": default_entity_name_scheme,
                                "status": {
                                    "enum": self.status_keys
                                },
                                "title": default_entity_name_scheme,
                                "links": {
                                    "type": "array",
                                    "items": [
                                        {
                                            "type": "object",
                                            "properties": {
                                                "url": {
                                                    "type": "string"
                                                },
                                                "name": {
                                                    "type": "string"
                                                }
                                            }
                                        }
                                    ]
                                }
                            },
                            "required": ['testname', 'status'],
                            "additionalProperties": True
                        }
                    ]
                }
            },
            "additionalProperties": True
        }

        self.end_of_test_suite=False
        self.test_suite_final_status = 'success'
        self.test_data = {}
        self.suite_links = []
        self._state = {}

    def _print_test_link(self, link):
        print('[OPERETO_HTML]<br><a href="{}"><font style="color: #222; font-weight: 600; font-size: 13px;">{}</font></a>'.format(link['url'], link['name']))


    def _append_to_process_log(self, pid, ppid, loglines, log_level='info'):
        log_request_data = {
            'sflow_id': self.sflow_id,
            'pflow_id': ppid,
            'agent_id': self.input['opereto_agent'],
            'product_id': self.input['opereto_product_id'],
            'data': []
        }
        count = 1
        for line in loglines:
            try:
                millis = int(round(time.time() * 1000)) + count
                log_request_data['data'].append({
                    'level': log_level,
                    'text': line.strip(),
                    'timestamp': millis
                })
            except Exception, e:
                print e
            count += 1

        self.client._call_rest_api('post', '/processes/{}/log'.format(pid), data=log_request_data,
                                       error='Failed to update test log (test pid = {})'.format(pid))

    def _check_source_alive(self):
        if self.next_check_source_alive>self.input['listener_frequency']*10:
            self.next_check_source_alive=0
            source_status = self.client.get_process_status(self.sflow_id)
            if source_status!='in_process':
                self.client.stop_process(pids=str(self.client.input['pid']), status='success')

        self.next_check_source_alive+=1

    def _modify_record(self, test_record):

        self._check_source_alive()

        testname = test_record['testname']
        test_input = test_record.get('test_input') or {}
        title = test_record.get('title') or testname
        status = test_record['status']
        test_links = test_record.get('links') or []
        test_ppid = test_record.get('ppid') or self.parent_pid
        test_pid = test_record.get('pid')
        if testname not in self._state:
            if not test_pid:
                test_pid = self.client.create_process('opereto_test_listener_record', testname=testname, title=title, test_input=test_input, pflow_id=test_ppid)
                self.client.wait_to_start(test_pid)
            self._state[testname] = {
                'ppid': test_ppid,
                'pid': test_pid,
                'status': 'in_process',
                'title': title,
                'test_output_md5': '',
                'summary_md5': '',
                'last_log_line': 1
            }
        else:
            test_pid = self._state[testname]['pid']

        if self._state[testname]['status'] not in self.result_keys:

            if status in self.result_keys:
                time.sleep(self.client.input['listener_frequency'])

            if title!=self._state[testname]['title']:
                ### TBD: add title change API call
                self._state[testname]['title']=title

            results_dir = os.path.join(self.test_results_dir, testname)
            if os.path.exists(results_dir):
                output_json_file = os.path.join(results_dir, 'output.json')
                log_file = os.path.join(results_dir, 'stdout.log')
                summary_file = os.path.join(results_dir, 'summary.txt')

                if os.path.exists(output_json_file):
                    output_json_md5 = get_file_md5sum(output_json_file)
                    with open(output_json_file, 'r') as of:
                        output_json = json.load(of)
                        if output_json_md5!=self._state[testname]['test_output_md5']:
                            self.client.modify_process_property('test_output', output_json, pid=test_pid)
                            self._state[testname]['test_output_md5'] = output_json_md5

                if os.path.exists(summary_file):
                    summary_md5 = get_file_md5sum(summary_file)
                    with open(summary_file, 'r') as sf:
                        summary = sf.read()
                        if summary_md5!=self._state[testname]['summary_md5']:
                            self.client.modify_process_summary(test_pid, summary)
                            self._state[testname]['summary_md5'] = summary_md5


                if os.path.exists(log_file):
                    with open(log_file, 'r') as lf:
                        count=1
                        loglines=[]
                        for line in lf.readlines():
                            if count>=self._state[testname]['last_log_line']:
                                if count>MAX_LOG_LINES_PER_PROCESS:
                                    message = 'Test log is too long. Please save test log in remote storage and add a link to it in Opereto log. See service info to learn how to add links to your tests.json file.'
                                    loglines.append('[OPERETO_HTML]<br><br><font style="width: 800px; padding: 15px; color: #222; font-weight: 400; border:2px solid red; background-color: #f8f8f8;">{}</font><br><br>'.format(message))
                                    break
                                loglines.append(line.strip())
                            count+=1
                        self._append_to_process_log(test_pid, test_ppid, loglines)
                        self._state[testname]['last_log_line']=count

            if status in self.result_keys:
                links=[]
                for link in test_links:
                    html_link = '[OPERETO_HTML]<br><a href="{}"><font style="color: #222; font-weight: 600; font-size: 13px;">{}</font></a>'.format(
                        link['url'], link['name'])
                    links.append(html_link)
                    self._append_to_process_log(test_pid, test_ppid, links)
                self.client.stop_process(test_pid, status=status)
                self._state[testname]['status']=status


    def process(self):

        def process_results():
            tests_json = os.path.join(self.test_results_dir, 'tests.json')
            if os.path.exists(tests_json):
                with open(tests_json, 'r') as tf:
                    self.test_data = json.load(tf)
                    all_tests_completed=True
                    try:
                        validator = JsonSchemeValidator(self.test_data, self.tests_json_scheme)
                        validator.validate()
                    except Exception, e:
                        print 'Invalid tests json file: {}'.format(e)
                        return

                    if 'test_records' in self.test_data:
                        for test_record in self.test_data['test_records']:
                            self._modify_record(test_record)
                            if test_record['status'] not in self.result_keys:
                                all_tests_completed=False

                    if 'test_suite' in self.test_data and all_tests_completed:
                        if 'status' in self.test_data['test_suite']:
                            if self.test_data['test_suite']['status'] in self.result_keys:
                                self.end_of_test_suite=True
                                self.test_suite_final_status=self.test_data['test_suite']['status']
                        if 'links' in self.test_data['test_suite']:
                            self.suite_links = self.test_data['test_suite']['links']
            if self.debug_mode:
                print 'Content of tests_json:'
                print json.dumps(self.test_data, indent=4)


        while(True):
            process_results()
            time.sleep(self.client.input['listener_frequency'])
            if self.end_of_test_suite:
                break

        print 'Content of tests_json:'
        print json.dumps(self.test_data, indent=4)

        for link in self.suite_links:
            self._print_test_link(link)

        if self.test_suite_final_status=='success':
            return self.client.SUCCESS
        elif self.test_suite_final_status=='failure':
            return self.client.FAILURE
        elif self.test_suite_final_status=='warning':
            return self.client.WARNING
        else:
            return self.client.ERROR


    def setup(self):
        pass

    def teardown(self):
        self._print_step_title('Opereto test listener stopped.')


if __name__ == "__main__":
    exit(ServiceRunner().run())
