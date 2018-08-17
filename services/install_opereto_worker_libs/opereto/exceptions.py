import json
from opereto.utils.osutil import is_ubuntu, is_root


class OperetoRuntimeError(Exception):
    def __init__(self,error=None, description=None, resources=[]):
        self.error = error or 'Failed to perform this operation, please check the logs for more details or retry later. If the problem consist, please contact opereto support.'
        self.description = description or ''
        self.resources = description or []

    def __str__(self):
        return json.dumps({'error' : self.error, 'description' : self.description, 'resources' : self.resources})


def raise_if_not_ubuntu():
    if not is_ubuntu():
        raise OperetoRuntimeError(error='This operation is currently support only Ubuntu distributions')


def raise_if_not_root():
    if not is_root():
          raise OperetoRuntimeError(error='This operation requires root privileges. Please run the agent with root user')