import os
import uuid
from osutil import zip_folder


def deploy_service(client, service_dir):
    zip_action_file = os.path.join('/tmp', str(uuid.uuid4())+'.action')
    zip_folder(zip_action_file, service_dir)
    print zip_action_file+'.zip'
    client.upload_service_version(service_zip_file=zip_action_file+'.zip')


def print_log_entries(client, pid):
    log_entries = client.get_process_log(pid)
    if log_entries:
        print 'Process log:'
        for entry in log_entries:
            print(entry['text'])


