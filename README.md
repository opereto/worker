## Opereto official worker lib

This is Opereto official python worker. It is a python virtualenv based allowing isolation of the worker libs and dependencies from other python packages that may be installed on the worker host or container. Opereto provides a set of out-of-the-box services depending on this worker library. Worker libs can be installed on standard host OS and on custom tool containers. Opereto standard worker stateful set is based on opereto/worker standard container (see the Dockerfile included in this package to learn more).

| Service                               | Description                                                                                |
| --------------------------------------|:------------------------------------------------------------------------------------------:| 
| services/install_opereto_worker_libs  | Install opereto python virtual environment library on a given host                         | 
| services/remove_opereto_worker_libs   | Remove opereto python virtual environment library on a given host                          | 
| services/opereto_test_listener        | A generic listener collecting test data and logs from test tools                           | 
| services/opereto_test_listener_record | A generic test record used by the Opereto test listener to store test data                 | 
| services/opereto_worker_statefulset   | Manages worker stateful sets used by Opereto as tools and operation processing endpoints   | 

See the [docs](https://docs.opereto.com) to learn more about packages.

### Prerequisits
* It requires Python 2.7+ to be installed on the target agent host. 

