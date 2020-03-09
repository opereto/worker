import os,sys, traceback
import platform

FAILURE=False


def install_opereto_lib():

    LIB_DIR = os.path.join(os.environ['opereto_workspace'], 'opereto')
    VIRT_ENV_DIR = os.path.join(os.environ['opereto_home'], 'operetovenv')

    per_os_module_to_install = {
        'rhel7.2': {
            'paramiko': 'paramiko==2.1.2'
        },
        'rhel6.9': {
            'PIL': 'Pillow==6.2.2',
        }
    }

    module_to_install = {
        'yaml' : 'pyyaml==3.13',
        'pyopereto': 'pyopereto==1.0.80',
        'requests': 'requests==2.19.1',
        'boto': 'boto==2.49.0',
        'paramiko': 'paramiko==2.4.1',
        'six': 'six==1.11.0',
        'sh': 'sh==1.12.14',
        'werkzeug': 'werkzeug==0.14.1',
        'psutil': 'psutil==0.7.0',
        'dateutil': 'python-dateutil==2.7.3',
        'jsonschema': 'jsonschema==2.6.0',
        'faker_schema': 'faker-schema==0.1.4',
        'docker': 'docker==3.1.4',
        'PIL': 'Pillow==2.9.0',
        'boto3': 'boto3==1.7.39',
        'httplib2': 'httplib2==0.11.3',
        'oauth2client': 'oauth2client==4.1.2',
        'apiclient': 'google-api-python-client==1.7.4',
        'junitparser': 'junitparser==1.2.2',
        'kubernetes':'kubernetes==5.0.0'
    }


    def get_current_os():
        (name, version,id) = platform.linux_distribution()
        return (name, version,id)

    def is_ubuntu():
        (name, version,id) = get_current_os()
        if name == 'Ubuntu':
            return True
        return False

    def is_windows():
        if platform.system() == 'Windows':
            return True
        return False

    def _remove_dir(dir):
        if os.path.exists(dir):
            if is_windows():
                _local("rmdir /s /q %s"%dir)
            else:
                _local("sudo rm -rf %s"%dir)

    def _create_dir_if_not_exists(dir):
        if not os.path.exists(dir):
            if is_windows():
                _local("mkdir %s" % dir)
            else:
                _local("sudo mkdir -p %s" % dir)
                _local('sudo chmod -R 777 ' + dir)

    def _copy_opereto_venv_contents(dir):
        if is_windows():
            WIN_LIB_DIR = LIB_DIR.replace("/","\\")
            _local("xcopy %s %s /q /i /e /Y" % (WIN_LIB_DIR, os.path.join(dir, 'opereto', 'venv')))
        else:
            _local("cp -rf %s %s" % (LIB_DIR, os.path.join(dir, 'opereto')))


    def _local(cmd, ignore=False):
        global FAILURE
        print cmd
        ret = os.system(cmd)
        if int(ret)!=0 and not ignore:
            print 'Command ended with exit code: {}'.format(int(ret))
            FAILURE=True
        return ret


    def _prepare_new_virtual_env(directory):
        os_name=None
        (name, version,id) = get_current_os()

        print 'Current OS: {} {}, {}'.format(name, version,id)
        if name=='Red Hat Enterprise Linux Server':
            os_name='rhel{}'.format(version)

        if os_name and per_os_module_to_install.get(os_name):
            module_to_install.update(per_os_module_to_install[os_name])

        if is_windows():
            _local('cd %s && virtualenv venv' % (directory), ignore=False)
            for import_name, module in module_to_install.items():
                _local('cd %s && pip install %s' % (os.path.join(directory,'venv', 'Scripts'), module), ignore=False)
                if _local('cd %s && python -c "import %s"' % (os.path.join(directory, 'venv', 'Scripts'), import_name)) != 0:
                    print >> sys.stderr, 'Python module [%s] is not installed.' % module

        else:
            _local('cd %s && virtualenv venv -p python2.7 && . venv/bin/activate && pip install --upgrade pip ; deactivate'%(directory),ignore=False)

            for import_name, module in module_to_install.items():
                _local('cd %s && . venv/bin/activate && pip install %s && deactivate'%(directory, module),ignore=True)
                if _local('cd %s && . venv/bin/activate && python -c "import %s" && deactivate'%(directory, import_name))!=0:
                    print >> sys.stderr, 'Python module [%s] is not installed.'%module


    def create_virtual_env(current_version_dir):
        _remove_dir(current_version_dir)
        _create_dir_if_not_exists(current_version_dir)
        _copy_opereto_venv_contents(current_version_dir)
        _prepare_new_virtual_env(current_version_dir)
        if not is_windows():
            _local('sudo chmod 777 -R %s'%current_version_dir)
            _local("sudo su -c 'echo \"export PYTHONPATH=%s\" >> %s'"%(current_version_dir,os.path.join(current_version_dir,'venv/bin/activate')))

    try:
        release=os.environ.get('opereto_service_version')

        ## check prerequisites
        if sys.version_info<(2,7):
            print >> sys.stderr,'Opereto microservices lib requires python 2.7 or higher.'
            return 2

        if is_ubuntu():
            (name, version,id) = get_current_os()
            install_list = 'sudo apt-get install -qy python-six curl python-setuptools gcc build-essential python-dev python-pip libffi-dev libssl-dev'
            _local(install_list,ignore=False)
            _local('sudo pip install virtualenv', ignore=False)

        elif is_windows():
            _local('pip install virtualenv', ignore=False)
            _local('pip install pyopereto')

        else:
            _local('sudo yum install -y python-virtualenv python-setuptools gcc libffi python-devel openssl-devel')
            _local('easy_install pip')

        if not is_windows():
            _local('sudo pip install pyopereto')

        current_version_dir= os.path.join(VIRT_ENV_DIR,release)
        create_virtual_env(current_version_dir)

        if FAILURE:
            return 3
        else:
            if os.environ.get('opereto_agent'):
                from pyopereto.client import OperetoClient
                c = OperetoClient()
                if c.input['standard_opereto_worker']:
                    c.modify_agent_property(c.input['opereto_agent'], 'opereto.worker', True)
            return 0

    except Exception, e:
        print traceback.format_exc()
        return 2

if __name__ == "__main__":
    exit(install_opereto_lib())

