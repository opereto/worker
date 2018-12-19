from opereto.exceptions import OperetoRuntimeError
from opereto.utils.osutil import make_directory
from junitparser import JUnitXml
import json, os

class JunitToOperetoResults(object):

    def __init__(self, source_path, dest_path):
        self.source_path = source_path
        self.dest_path = dest_path
        self.tests = {
            'test_records': []
        }
        self.suite_status = 'success'


    def parse(self):

        try:
            xml = JUnitXml.fromfile(self.source_path)
            if int(xml.errors)>0 or int(xml.failures)>0:
                self.suite_status='failure'


            for case in xml:
                summary=''
                status=None
                result = case.result
                if not result:
                    status = 'success'
                elif result._tag in ['failure', 'error']:
                    status = result._tag
                    summary = result.message

                if status:
                    testname = case.name
                    testcase_dict={
                        'testname': testname,
                        'title': testname,
                        'status': status
                    }
                    stdout = case.system_out
                    stderr = case.system_err
                    # classname = case.classname
                    # duration = case.time
                    self.tests['test_records'].append(testcase_dict)

                    def _modify_output_file(file, data):
                        with open(file, 'w') as of:
                            of.write(data)

                    ## create directory structure
                    if summary or stdout or stderr:
                        make_directory(self.dest_path)
                        make_directory(os.path.join(self.dest_path,testname))
                        if summary:
                            summary_file = os.path.join(self.dest_path,testname, 'summary.txt')
                            _modify_output_file(summary_file,summary)
                        if stdout:
                            stdout_file = os.path.join(self.dest_path,testname, 'stdout.log')
                            _modify_output_file(stdout_file, stdout)
                        if stderr:
                            stderr_file = os.path.join(self.dest_path,testname, 'stderr.log')
                            _modify_output_file(stderr_file, stderr)


            if self.tests['test_records']:
                tests_json_file = os.path.join(self.dest_path, 'tests.json')
                with open(tests_json_file, 'w') as tf:
                    tf.write(json.dumps(self.tests))
                    self.tests['test_suite']={'status': self.suite_status}

        except Exception, e:
            raise OperetoRuntimeError(error='Failed to parse junit results: {}'.format(str(e)))





