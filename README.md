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


#### Opereto worker container
To run opereto worker as a container:

* fetch opereto worker image
```
docker pull opereto/worker
```

* create credential env file
```
opereto_host=https://OPERETO_URL
opereto_user=OPERETO_USERNAME
opereto_password=OPERETO_PASSWORD
opereto_agent=my-agent-name

```

* run the worker container
```
docker run -d --restart=always --env-file opereto_env/opereto.env opereto/worker
```

For more information, see: http://help.opereto.com/support/solutions/articles/9000001855-install-and-run-agents

You can also extend opereto Dockerfile to create your own custom workers while still including the Opereto worker python
virtualenv to remain compatible with opereto official packages

```
FROM opereto/worker

your docker file directives.. 
(please make sure not to override opereto agent command. Avoi dspecifying CMD or ENTRYPOINT in your custom docker worker)
...  
...

```



