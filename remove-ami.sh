#!/bin/bash
# chkconfig: 2345 96 14

region_name=eu-west-1
profile=$1
ami_id=$2
temp_snapshot_id=''

if [[ $1 == '-h' || $1 == "--help" ]]
then
  echo $0 profile-name ami-id
  exit 0
fi

if [[ $# != 2 ]]
then 
  echo $0 profile-name ami-id
  exit 0
fi

my_array=( $(aws ec2 describe-images --profile $profile --image-ids $ami_id --region $region_name  --output text --query 'Images[*].BlockDeviceMappings[*].Ebs.SnapshotId') )

echo "Deregistering AMI: "$ami_id
aws ec2 deregister-image --profile $profile --image-id $ami_id --region $region_name

echo "Removing Snapshot"

for snapshot in "${my_array[@]}"
do
	echo "Deleting Snapshot: "$snapshot
	aws ec2 delete-snapshot --profile $profile --snapshot-id $snapshot --region $region_name
done
