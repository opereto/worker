This service is a generic task runner allowing to create and teardown a remote agent worker (or use an existing one) and run one or more services on it.
The service gets a worker config json and task runner list of services to perform on the worker. In case of test tools, it gets a pre-defined test results parser service as an input. The parser service must setisfy Opereto test result parser requirements. 


#### Service success criteria
Success if all tasks end with exit code 0. Otherwise, failure.

#### Dependencies
* Opereto worker virtual environment
