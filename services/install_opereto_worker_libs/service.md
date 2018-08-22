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


