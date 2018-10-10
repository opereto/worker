## Opereto official worker lib

This is the Opereto official worker package. It is required to be installed on a given agent host in order to run most of Opereto open-source service packages. The worker is based on python virtual environment to allow isolation of automation code running on a given agent host and other python programs running on that host. 
The package includes two services:

| Service                               | Description                                         |
| --------------------------------------|:---------------------------------------------------:| 
| services/install_opereto_worker_libs  | Install opereto python virtual environment library  | 
| services/remove_opereto_worker_libs   | Remove opereto python virtual environment library   | 


### Prerequisits
* It requires Python 2.7+ to be installed on the target agent host. 

### Service packages documentation
* [Learn more about automation packages and how to use them](http://help.opereto.com/support/solutions/articles/9000152583-an-overview-of-service-packages)
* [Learn more how to extend this package or build custom packages](http://help.opereto.com/support/solutions/articles/9000152584-build-and-maintain-custom-packages)


### Opereto worker container
To run opereto worker as a container:

* fetch opereto worker image
```console
docker pull opereto/worker
```


* run the worker container
```console
docker run -d --restart=always -e opereto_host='OPERETO_HOST_URL' -e opereto_user='OPERETO_USERNAME' -e opereto_password='OPERETO_PASSWORD' -e agent_name='AGENT_UUID' opereto/worker
```
For example:
```console
docker run -d --restart=always -e opereto_host='https://10.0.0.1' -e opereto_user='john' -e opereto_password='mypass123' -e agent_name='my_new_agent' opereto/worker
```

For more information, see: http://help.opereto.com/support/solutions/articles/9000001855-install-and-run-agents

You may also extend opereto Dockerfile to create your own custom workers while still including the Opereto worker python
virtualenv to remain compatible with opereto official packages

```
FROM opereto/worker

your docker file directives.. 
(please make sure not to override opereto agent run command. Avoid specifying CMD or ENTRYPOINT in your custom docker worker)
...  
...

```



