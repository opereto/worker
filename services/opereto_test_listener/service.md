Opereto test listener can be used by any test tool wrapper service executed via Opereto. It listens to a given results directory and creates child processes in Opereto for every test record detected including its test I/O, log, summary and status.
You may add Opereto test results listener to your test tool wrapper code as follows: 

1. Create a test result directory
2. Invoke the Opereto test results listener service of your wrapper code providing the path to that directory
3. Make sure to place all test results in that directory in the structure specified bellow

You may process and save the results at the end of all test execution and then invoke the listener or invoke the listener right in the begining and design your test tool wrapper code to update the test results directory periodically. 
The listener will collect and index test results delta changes at runtime whenever the results directory content changes.

### starting the listener

```python
from pyopereto.client import OperetoClient
import os 

client = OperetoClient()

my_result_dir = os.path.join(client.input['opereto_workspace'], 'test-result')  ## will use the current wrapper workspace
os.mkdir(my_result_dir)
client.create_process(service='opereto_test_listener', title='Invoking test listener..', test_results_path=my_result_dir)

```
See also: [running a service](/opereto-framework/automation_services/#running-a-service)

### stopping the listener
The listener will not stop untill one of the following events occurs:
1. The tests.json file includes a specific test_suite status specification (see bellow example) 
1. The wrapper process ends
1. The wrapper explicitly stops it 
```
client.stop_process(listener_process_pid, status='success')
```

### results directory structure

Following is the structure specification required by Opereto test results listener:

```angularjs
path/to/test/results/directory/
    tests.json                     
    test_1:                        
        output.json
        log.txt
        summary.txt
    test_2:                        
        output.json
        log.txt
        summary.txt
    ...
```


### tests.json

```json
{
    "test_suite": {               
        "status": "",
        "links": []
    },
    "test_records": [
        {
            "testname": "test_1",             
            "status": "success",              
            "test_input": {
                "base_url": "https://....",
                "testmode": "multizone"
                
                
            },
            "links": [
                {
                    "url": "",
                    "name": ""
                }
            ]
            
        }
                
    ]
}
```


tests.json scheme must satisfy the following constraints:


| Key   | Mandatory | Value / Constraints |
|---------------|-------------|-------|
| testname | Yes |  Start with lower_case and include the following chars only: [a-zA-Z0-9-_]|
| title | No | A display name for the test. If not provided, the test_id will be used. | 
| status | Yes | Any of the following: [success, failure, warning, error, timeout, terminated, in_process,registered] | 
| links	| No | A list of link maps. Each entry includes a URL and display name. Links are useful adding references to zip files, logs and other test output data stored on remote storage.  | 
| test_input | No | Any valid JSON representing the test input | 



#### Service success criteria
Success if no test_suite status is provided in the tests.json. Otherwise, takes the test_suite status.

#### Assumptions/Limitations
1. Opereto creates new test records bases on the tests.json entries. The additional files directory per test is optional and used to add additional test data such as test I/O, log and summary. 
1. Please note that in case of changes in one of the following files: input.json, output.json and summary.txt, Opereto listener will override the previous data collected.
1. As for the log.txt, Opereto will only update the new entries (delta from previous updates) in the log. This means that your test tool wrapper code may append entries to the test log file during runtime.

#### Dependencies
* Opereto worker virtual environment