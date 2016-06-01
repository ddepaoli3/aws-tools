Repository containing script about aws tools

# instances_table
Using boto3 print a table of all instances.
Using it:
```
python instances_table -p "profile_name" -o weblike|securitygroup
``` 
_profile_name_ must be set in ~/.aws/credentials, otherwise use default one

* weblike print table similar to ec2 web interface
* securitygroup: prit instances and its security group

# rds_list
Print a list of rds databases in a given region
```
python rds_list.py -p "profile_name"
```
