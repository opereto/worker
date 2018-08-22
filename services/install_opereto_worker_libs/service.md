This service installs/updates Opereto worker libraries on a given remote agent host. 
Opereto worker libraries are packed as a python virtual environment located under the agent installation directory. 

#### Service success criteria
Success if Opereto worker libraries are properly installed. Otherwise, Failure.

#### Assumptions/Limitations
* Currently supports only Linux distributions as follows: Ubuntu 14.04 Trusty, Ubuntu 16.04 Xenial, RHEL/Centos 7 and above
* Requires that agent user will have sudo permissions
* This service installs the following packages on the host operating system

```
## Ubuntu 
OS: python-six curl python-setuptools gcc build-essential python-dev python-pip libffi-dev libssl-dev
Python: virtualenv, pyopereto

## Rhel/Centos:
OS: python-virtualenv python-setuptools gcc libffi python-devel openssl-devel
Python: pip, pyopereto
```

#### Dependencies
No dependencies.



#### Opereto worker container
On you docker machine:

* fetch opereto worker image
```
docker pull opereto/worker
```

* create credential env file
```
opereto_host=https://OPERETO_URL
opereto_user=OPERETO_USERNAME
opereto_password=OPERETO_PASSWORD
agent_name=my-agent-name

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



