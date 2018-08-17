import docker
import sys
import time
from opereto.exceptions import OperetoRuntimeError
import docker.errors

class Dockereto(object):

    def __init__(self):
        self.docker_client = docker.from_env()


    def setup_container(self, image_name, **kwargs):

        try:
            container = self.docker_client.containers.run(image_name, detach=True, **kwargs)
        except docker.errors.ImageNotFound :
            raise OperetoRuntimeError(error='Container image {} not found.'.format(image_name))
        except Exception,e:
            raise OperetoRuntimeError(error=str(e))
        print 'New container ID is: {}'.format(container.id)
        print 'Waiting for container to be ready..'

        for i in range(12):
            print 'Container status is: {}'.format(container.status)
            if container.status in ['exited', 'paused']:
                time.sleep(2)
                print container.logs(stderr=True, stdout=True)
                raise OperetoRuntimeError
            elif container.status in ['created', 'running']:
                print container.logs(stderr=True, stdout=True)
                break
            else:
                time.sleep(5)

        for i in range(12):
            status = self.docker_client.containers.get(container.id).status
            if status=='running':
                print 'Container is up and running..'
                break
            time.sleep(5)

        return container


    def teardown_container(self, container_id, **kwargs):

        try:
            container = self.docker_client.containers.get(container_id)
        except docker.errors.NotFound:
            raise OperetoRuntimeError(error='Container not found on this agent host.')
        except Exception,e:
            raise OperetoRuntimeError(error=str(e))

        container.remove(force=True)

        for i in range(12):
            try:
                self.docker_client.containers.get(container.id)
                time.sleep(5)
            except docker.errors.NotFound:
                print 'Container was removed successfully'
                return
            except Exception, e:
                raise OperetoRuntimeError(error=str(e))

        raise OperetoRuntimeError(error='Failed to remove container.')



    def get_container(self, container_id):
        container = self.docker_client.containers.get(container_id)
        return container


    def cmd_exec(self, container_id, command, **kwargs):
        container = self.get_container(container_id)
        (exit_code, output) = container.exec_run(command, **kwargs)
        try:
            out = unicode(output, 'utf-8')
        except TypeError:
            out=output

        if out is not None:
            max_property_value_length = 99000
            if len(out) > max_property_value_length:
                err_msg = 'Command standard output stream exceeds the maximum allowed property value length'
                out_trimed = out[0:max_property_value_length]
                print >> sys.stderr, err_msg
                out = out_trimed
        return (exit_code, out)
