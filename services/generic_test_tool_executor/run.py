from opereto.helpers.services import ServiceTemplate
from opereto.utils.validations import JsonSchemeValidator, validate_dict
from opereto.exceptions import *
from pyopereto.client import OperetoClient
from opereto.exceptions import *

class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        self.client = OperetoClient()
        ServiceTemplate.__init__(self, **kwargs)

    def validate_input(self):

        input_scheme = {
            "type": "object",
            "properties": {
                "testing_tool_command": {
                    "type": "string",
                    "minLength": 1
                },
                "report_file_path": {
                    "type": "string",
                    "minLength": 1
                },
                "tool_valid_exit_codes": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9_.-]*((,{1})[a-zA-Z0-9_.-]+)*"
                },
                "upload_report_to_storage": {
                    "type": "boolean"
                },
                "storage_config": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "minLength": 1
                        },
                        "source_path_input_property_name": {
                            "type": "string",
                            "minLength": 1
                        },
                        "storage_url_output_property_name": {
                            "type": "string",
                            "minLength": 1
                        },
                        "input": {
                            "type": "object",
                        },
                        "title": {
                            "type": "string",
                            "minLength": 1
                        },
                        "required": ['service_id', 'input'],
                        "additionalProperties": True
                    }
                },
                "required": ['testing_tool_command', 'upload_report_to_storage'],
                "additionalProperties": True
            }
        }

        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()

        if self.client.input['upload_report_to_storage'] and not self.client.input['storage_config']:
            raise OperetoRuntimeError(error='Invalid storage parameters')

    def process(self):

        def execute_tool():
            tool_execution_command = self.client.input['testing_tool_command']
            cmd_pid = self.client.create_process('shell_command', command=tool_execution_command,
                                                 valid_exit_codes=self.client.input['tool_valid_exit_codes'])
            if not self.client.is_success(cmd_pid):
                raise OperetoRuntimeError(error='Failed to execute tool: %s' % tool_execution_command)

        def upload_to_storage():
            report_file_path = self.client.input['report_file_path']
            if report_file_path:
                print 'Report file path: {}'.format(report_file_path)

            storage_config = self.client.input['storage_config']

            source_path_input_property_name = storage_config.get('source_path_input_property_name') or 'source_path'

            storage_config['input'].update({source_path_input_property_name: report_file_path})

            cmd_pid = self.client.create_process(storage_config['service_id'], title=storage_config.get('title'),
                                                 **storage_config['input'])

            if not self.client.is_success(cmd_pid):
                raise OperetoRuntimeError(error='Could not upload report to storage')

            storage_url_output_property_name = storage_config.get('storage_url_output_property_name') or 'storage_url'
            report_storage_path = self.client.get_process_properties(pid=cmd_pid, name=storage_url_output_property_name)

            if (report_storage_path):
                print '[OPERETO_HTML]<a target="_blank" href="' + report_storage_path + '">' + report_storage_path + '</a>'
                print '\n\n'

        # Execute tool
        execute_tool()

        # Upload results to storage
        if self.client.input['upload_report_to_storage']:
            upload_to_storage()

        self.client.logger.info(msg='Tool execution finished successfully')
        return self.client.SUCCESS

    def setup(self):
        pass

    def teardown(self):
        pass


if __name__ == "__main__":
    exit(ServiceRunner().run())
