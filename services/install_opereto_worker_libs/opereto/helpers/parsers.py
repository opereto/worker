from opereto.exceptions import OperetoRuntimeError
from opereto.utils.osutil import make_directory
from junitparser import JUnitXml, TestSuite
import collections
import json, os
import re

class JunitToOperetoResults(object):

    def __init__(self, source_path, dest_path):
        self.source_path = source_path
        self.dest_path = dest_path
        self.tests = {
            'test_records': []
        }

        make_directory(self.dest_path)

    def _print_testcase(self, text, color):
        return '[OPERETO_HTML]<font style="color: {}; font-size: 15px; font-weight: 600;">{}</font><br>\n'.format(color, text)

    def parse(self, debug_mode=False):
        self.tests_data = {}

        try:
            def parser_suite(suite):

                def _modify_output_file(file, data):
                    with open(file, 'w') as of:
                        of.write(data)

                test_records = collections.OrderedDict()

                if debug_mode:
                    props = {
                        "name": suite.name,
                        "time": suite.time,
                        "timestamp": suite.timestamp,
                        "tests": suite.tests,
                        "failures": suite.failures,
                        "errors": suite.errors,
                        "skipped": suite.skipped
                    }
                    print('DEBUG: {}'.format(props))

                if int(suite.tests)>0:
                    self.suite_status = 'success'
                if int(suite.failures) > 0:
                    self.suite_status = 'failure'
                if int(suite.errors) > 0:
                    self.suite_status = 'error'

                def _escape_name(name):
                    return re.sub('[^0-9a-z-_]+', '-', name).lower()

                for case in suite:
                    if case.classname:
                        testname = _escape_name(case.classname)
                    else:
                        testname = _escape_name(case.name)

                    summary = ''
                    result = case.result
                    status = 'success'
                    if result:
                        status = result._tag
                        if status in ['failure', 'error']:
                            status = result._tag
                        else:
                            status = 'warning'

                        try:
                            summary = '{}<BR>{}'.format(result.message, result._elem.text)
                        except:
                            try:
                                summary = '{}'.format(result.message)
                            except:
                                summary = ''

                    stdout = case.system_out
                    stderr = case.system_err

                    if testname not in test_records:
                        test_dict={
                            'testname': testname,
                            'title': testname,
                            'status': status
                        }
                        test_records[testname] = test_dict

                    if testname not in self.tests_data:
                        self.tests_data[testname]=[]

                    if summary or stdout or stderr:
                        make_directory(os.path.join(self.dest_path, testname))
                    self.tests_data[testname].append({
                        'name': case.name,
                        'stdout': stdout,
                        'stderr': stderr,
                        'summary': summary,
                        'duration': str(case.time),
                        'status': status
                    })

                self.tests['test_records']=test_records.values()

                for tn, cases in self.tests_data.items():
                    tn_summary = ''
                    tn_log_data = ''
                    for case in cases:
                        if case['summary']:
                            tn_summary+='<b>{}</b><BR>{}<BR>'.format(case['name'],case['summary'])

                        if case['stdout'] or case['stderr']:
                            if case['status'] == 'success':
                                tn_log_data += self._print_testcase(case['name'], '#0075EA')
                            elif case['status'] in ['failure', 'error']:
                                tn_log_data += self._print_testcase(case['name'], '#EF5000')
                            else:
                                tn_log_data += self._print_testcase(case['name'], '#333333')

                            if case['stdout']:
                                tn_log_data += '{}\n'.format(case['stdout'])
                            if case['stderr']:
                                tn_log_data += '{}\n'.format(case['stderr'])

                        if case['status']=='failure' and test_records[tn]['status']!='error':
                            test_records[tn]['status']='failure'
                        if case['status']=='error':
                            test_records[tn]['status']='error'

                    if tn_summary:
                        summary_file = os.path.join(self.dest_path, tn, 'summary.txt')
                        _modify_output_file(summary_file, tn_summary)
                    if tn_log_data:
                        stdout_file = os.path.join(self.dest_path, tn, 'stdout.log')
                        _modify_output_file(stdout_file, tn_log_data)


            xml = JUnitXml.fromfile(self.source_path)
            if isinstance(xml, TestSuite):
                parser_suite(xml)
            else:
                for suite in xml:
                    parser_suite(suite)

            if self.tests['test_records']:
                tests_json_file = os.path.join(self.dest_path, 'tests.json')
                self.tests['test_suite'] = {'status': self.suite_status}
                with open(tests_json_file, 'w') as tf:
                    tf.write(json.dumps(self.tests, indent=4))

        except Exception, e:
            raise OperetoRuntimeError(error='Failed to parse junit results: {}'.format(str(e)))

