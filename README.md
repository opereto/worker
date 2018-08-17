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

