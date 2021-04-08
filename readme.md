# Simple Terraform Policy Tool
*First off I would like to acknowledge Thomas Ruble who originally developed this script.*

There are are a couple of libraries/tools that will validate terraform scripting but those libraries and  policy definitions are very complex. This tool utilizes the [Voluptuous library](https://pypi.org/project/voluptuous/) and standard python scripting to validate terraform.  

## Requirements
* Python 3.7+
* [Voluptuous library](https://pypi.org/project/voluptuous/) 


## Usage

The main script (`main.py`) applies a _policy_ (`policy.py`) to a JSON-serialized Terraform plan.  

In order to run the Python program, you must first create this plan as shown below:
```bash
# create the binary plan
terraform plan -out plan.bin > /dev/null
# serialize the plan into json
terraform show -json plan.bin > plan.json
# clean up the artefact
rm plan.bin
```

Now that a `plan.json` has been generated, you can run the policy engine against that plan:

```bash
python main.py plan.json
```

The program will output messages for all Terraform resources that break the policy.  It will only exit successfully if there are no errors.

In a pipeline, you may want to program to exit successfully no matter the errors.  In this case, run it in _warning_ mode.

```bash
python main.py plan.json --warn
```

## Install
* Make sure you have python 3 installed
* run pip install to install voluptuous library
  ```bash
  pip install -r requirements.txt
  ```


## Demo

To test, first run `terraform init` in the `tf_examples` directory to init terraform. In the `tf_examples` directory run the `make_plan.sh` to generate a json version of the plan. The `make_plan.sh` script does the following:
```bash
terraform plan -out plan.bin > /dev/null
terraform show -json plan.bin > plan.json
rm plan.bin
```

After the json plan is generated run the python script to validate the plan against the configured policy:
```bash
python main.py tf_examples/plan.json
```
After running the above command you should see the following errors emitted:
```
google_bigquery_dataset dataset_no_cmek : BigQuery must use CMEK for dictionary value @ data['google_bigquery_dataset']['default_encryption_configuration']
google_compute_subnetwork subnet-with-no-logging : Subnets must have VPC Flow Logs enabled for dictionary value @ data['google_compute_subnetwork']['log_config']
google_game_services_game_server_cluster default : Forbidden resource for dictionary value @ data['google_game_services_game_server_cluster']
google_healthcare_dataset default : Forbidden resource for dictionary value @ data['google_healthcare_dataset']
google_kms_key_ring asia : Key Ring location must be within specific regions for dictionary value @ data['google_kms_key_ring']['location']
google_kms_key_ring us-bad : Key Ring location must be within specific regions for dictionary value @ data['google_kms_key_ring']['location']
google_project project_missing_label : expected a dictionary for dictionary value @ data['google_project']['labels']
google_redis_instance redis_no_ha : Redis instance must be in HA configuration for dictionary value @ data['google_redis_instance']['tier']
google_sql_database_instance instance_with_replication_type : required key not provided @ data['google_sql_database_instance']['settings'][0]['backup_configuration']
google_sql_database_instance sql_no_key : required key not provided @ data['google_sql_database_instance']['settings'][0]['backup_configuration']
google_storage_bucket bucket : expected a dictionary for dictionary value @ data['google_storage_bucket']['labels']
google_storage_bucket bucket_no_cmek : length of value must be at least 1 for dictionary value @ data['google_storage_bucket']['encryption']
```


## Design

Policies are implemented in the [Voluptuous](https://pypi.org/project/voluptuous/) library.  This library is a stream-lined tool for defining schemas for data structures.  The policies are run against all resources in the Terraform plan that are going to be created or updated.

Resources are specified in the `schema` object found in `policy.py`. 

For an example:

```python
# make_schema() is defined in the policy.py file
schema = make_schema({
    'google_compute_firewall': {
        'enable_logging': True
})
```

This is a schema which runs a policy against one kind of Terraform resource: the `google_compute_firewall`.  Every key declared in the resource block is *required* and must match the rule given.  In this case, a `google_compute_firewall` would fail if either the key `enable_logging` is missing or if `enable_loging = false`.

You may add additional helper messages to provide meaningful error feedback:

```python
from voluptuous import Msg

schema = make_schema({
    'google_compute_firewall': {
        'enable_logging': Msg(True, 'Logging must be enabled for all firewalls')
    }
})
```

With this improvement, a resources that has `enable_logging = false` will fail with the helpful error message.

### Forbidden resources

To forbid resources, simply set them up with a validator function that always fails.

```python
from voluptuous import Invalid

def forbidden(_):
    raise Invalid('Resource is forbidden')

schema = make_schema({
    'google_healthcare_dataset': forbidden
})
```

### Custom validation functions ###
In the policy.py script the google_project resource requires a project_id to be defined. Additionally there is a call to valid_project_id to perform additional validation. This is a normal python function. 
```python
"google_project": {
    "project_id": valid_project_id,
    Required("labels"): Schema({
        Required("product"): anything,
        Required("env"): anything,
    #    Required("newlabel"): anything,
    })
},
```

Note this function is just doing basic validation of project_id but you now have the freedom to do whatever type of validation that is neccessary.
```python
def valid_project_id(project_id):
    # Terraform resource values are lists -- get head of list
    if len(project_id) > 30:
        raise Invalid("Project ID greater than 30 chars")
    project_id_re = re.compile(r"^[a-z0-9]*\-[a-z0-9]*\-[a-z0-9]*\-[a-z0-9]*$")

    # Bad format
    # project_id_re = re.compile(r"^[a-z0-9]*\-[a-z0-9]*\-[a-z0-9]$")
    if not re.match(project_id_re, project_id):
        raise Invalid("Project ID invalid against regex.")
```

### Objects within Objects
In the following resource definition:
```python
resource "google_project" "project" {
  name       = "My Project"
  project_id = "apex-docmgmt-dev-1111"
  org_id     = "1234567"

  labels = {
    product = "docmgmt"
    env = "dev"
  }
}
```
labels contains an object. In order to validate the additional keys within the label object a subsequent schema block is defined.
```python
"google_project": {
    "project_id": valid_project_id,
    Required("labels"): Schema({
        Required("product"): anything,
        Required("env"): anything,
    #    Required("newlabel"): anything,
    })
},
```

