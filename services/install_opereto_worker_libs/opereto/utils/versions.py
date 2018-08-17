import re
from distutils.version import LooseVersion as V

def valid_version(version):
    version_pattern = '^\d+\.\d+\.\d+$'
    ver_rx =re.compile(version_pattern)
    if not ver_rx.match(version):
        raise Exception, 'version must be provided in the form: {} (e.g. 1.1.10)'.format(version_pattern)



def is_higher_version(ver1, ver2, include_equal=False):

    if not ver1 or not ver2:
        return False
    v1 = V(ver1)
    v2 = V(ver2)
    if v1>v2:
        return True
    if include_equal and v1==v2:
        return True
    return False


def _last_version_in_list(list):
    max=None
    if list:
        for key in list:
            if not max:
                max=key
            elif is_higher_version(key, max):
                max=key
    return max