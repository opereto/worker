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