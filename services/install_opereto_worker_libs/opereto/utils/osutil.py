import re
import tarfile
import os
import requests
import shutil
import tempfile
import random
import string
from zipfile import ZipFile as zip
import hashlib
import platform
from opereto.utils.shell import run_shell_cmd

DIST_RHEL6 = 'rhel6'
DIST_RHEL7 = 'rhel7'
DIST_CENTOS6 = 'centos6'
DIST_CENTOS7 = 'centos7'
DIST_TRUSTY = 'trusty'
DIST_XENIAL= 'xenial'

centos_dist = [DIST_CENTOS6, DIST_CENTOS7]
rhel_dist = [DIST_RHEL6, DIST_RHEL7]
ubuntu_dist = [DIST_TRUSTY, DIST_XENIAL]


def is_root():
    return os.geteuid() == 0


def get_temp_file_name():
    return tempfile.mkdtemp()

def make_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def move_file_or_dir(src, dst):
    if os.path.exists(src):
        shutil.move(src, dst)

def copy_file(src, dst, chmod=None):
    shutil.copyfile(src, dst)
    if chmod:
        os.chmod(dst,chmod)

def copy_file_if_exists(src, dst, chmod=None):
    if os.path.exists(src):
        copy_file(src, dst)
        if chmod:
            os.chmod(dst,chmod)

def delete_file_if_exists(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

def remove_directory_if_exists(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)


def download_from_url(url, target_dir=None, local_filename=None, username=None, password=None):
    if not local_filename:
        local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True, verify=False, auth=(username, password) if username is not None else None)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    if target_dir:
        target_file = os.path.join(target_dir, local_filename)
        shutil.move(local_filename, target_file)
        local_filename = target_file
    return local_filename


def replace_text_in_file(file, regexp, text):
    with open(file, 'r') as f:
        data = f.read()
    f.close()
    new_text = re.sub(regexp, text, data)
    if new_text:
        with open(file, 'w') as f:
            f.write(new_text)


def append_to_file(file, text):
    with open(file, 'a') as f:
        f.write(text)

def override_text_in_file(file, text):
    with open(file, 'w') as f:
        f.write(text)


def get_text_from_file(file, regexp):
    with open(file, 'r') as f:
        text = f.read()
    return get_text_from_data(text,regexp)


def delete_text_from_file(file, regexp):
    with open(file, 'r') as f:
        text = f.read()
    new_text = re.sub(regexp, '', text)
    if new_text:
        with open(file, 'w') as f:
            f.write(new_text)
        f.close()

def get_text_from_data(text,regexp):
    m = re.search(regexp, text)
    if m:
        return m.group(0)
    return None


def open_tgz_file(file, target_dir):
    tar = tarfile.open(file)
    tar.extractall(target_dir)
    tar.close()


def extract_zip_file(file, extract_dir):
    z = zip(file)
    for f in z.namelist():
        if f.endswith('/'):
            os.makedirs(os.path.join(extract_dir,f))
        else:
            z.extract(f, extract_dir)


def generate_random_key(length=15):
    if length<=36:
        char_set = string.ascii_uppercase + string.digits
        return ''.join(random.sample(char_set,length))
    else:
        raise Exception, 'max allowed length is 36'


def get_file_md5sum(file):
    md5 = hashlib.md5()
    with open(file,'rb') as f:
        for chunk in iter(lambda: f.read(8192), ''):
            md5.update(chunk)
    return md5.hexdigest()


def get_data_md5sum(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()

def get_data_sha256(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


def read_file_safely(file):
    data=''
    with open(file,'rb') as f:
        for chunk in iter(lambda: f.read(8192), ''):
            data+=chunk
    return data


def get_os_distribution():
    return platform.linux_distribution()


def is_ubuntu():
    return get_platform_name() in ubuntu_dist


def is_centos():
    return get_platform_name() in centos_dist


def is_rhel():
    return get_platform_name() in rhel_dist


# get platform name
def get_platform_name():
    (name, version,id) = platform.linux_distribution()
    if name == 'Ubuntu':
        if id=='xenial':
            return DIST_XENIAL
        elif id=='trusty':
            return DIST_TRUSTY

    elif name == 'Red Hat Enterprise Linux Server':
        if version.startswith('6'):
            return DIST_RHEL6
        elif version.startswith('7'):
            return DIST_RHEL7

    elif name.startswith('CentOS'):
        if version.startswith('6'):
            return DIST_CENTOS6
        elif version.startswith('7'):
            return DIST_CENTOS7

    raise Exception('Unable to detect distribution: name=%s, version=%s, id=%s' % (name, version,id))


def install_package_cmd(package_name, sudo=True, update_sources=False):
    cmd=''
    if is_ubuntu():
        if update_sources:
            cmd+='apt-get update ; '
        cmd += 'apt-get install -y {}'.format(package_name)
    else:
        if update_sources:
            cmd+='yum update ; '
        cmd = 'yum install -y {}'.format(package_name)

    if sudo:
        cmd = 'sudo -iEn '+cmd

    (exc, out, error) = run_shell_cmd(cmd)
    return exc, out, error


def remove_package_cmd(package_name, sudo=True):
    if is_ubuntu():
        cmd = 'apt-get purge -y {}'.format(package_name)
    else:
        cmd = 'yum remove -y {}'.format(package_name)

    if sudo:
        cmd = 'sudo -iEn '+cmd

    (exc, out, error) = run_shell_cmd(cmd)
    return exc, out, error



