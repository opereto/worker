This service executes a given test tool, and, if selected, upload the report to storage.
The uploading to storage is done using any selected storage service, and passing the parameters in the storage_config json input property.
For example, you can use for it Opereto's "aws_save_to_s3" service (which is part of the Opereto AWS Services package) passing the needed parameters (see service documentation for help).
Example of the storage_config json input property:
```json
{
"storage_config": {
      "service_id": "aws_save_to_s3",
      "source_path_input_property_name": "source_path",
      "storage_url_output_property_name": "storage_url",
      "input": {
            "aws_access_key": "GLOBALS.opereto_aws_services-aws_access_key",
            "aws_secret_key": "GLOBALS.opereto_aws_services-aws_secret_key",
            "bucket_name": "bucket_name",
            "content_type": "text/plain",
            "create_bucket": true,
            "make_public": false,
            "presigned_url_expiry": 2592000,
            "target_path": "opereto"
      },
      "title": "Upload report to AWS S3"
    }
}
```
* source_path_input_property_name - name of the property in the storage service containing the path to the report to be uploaded. If not provided, default value is 'source_path'
* storage_url_output_property_name - name of the property in which the storage service returns the path to the uploaded report. If not provided, default value is 'storage_url'

#### Service success criteria
Success if command to execute exists, is accessible and its execution was successful.
If valid_exit_codes property is provided, then the process will be successful only if the return code is one of the valid_exit_codes.

#### Assumptions/Limitations
If uploading the tool report to storage, selected service must be provided with the relevant properties as explained above

#### Dependencies
* Opereto worker virtual environment