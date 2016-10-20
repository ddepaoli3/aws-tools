#!/usr/bin/env python

import json
import sys
import boto3
from datetime import datetime
from json import JSONDecoder
from json import JSONEncoder
import argparse
import pprint

class DateTimeDecoder(json.JSONDecoder):

    def __init__(self, *args, **kargs):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object,
                             *args, **kargs)
    
    def dict_to_object(self, d): 
        if '__type__' not in d:
            return d

        type = d.pop('__type__')
        try:
            dateobj = datetime(**d)
            return dateobj
        except:
            d['__type__'] = type
            return d

class DateTimeEncoder(JSONEncoder):
    """ Instead of letting the default encoder convert datetime to string,
        convert datetime objects into a dict, which can be decoded by the
        DateTimeDecoder
    """
        
    def default(self, obj):
        if isinstance(obj, datetime):
            return {
                '__type__' : 'datetime',
                'year' : obj.year,
                'month' : obj.month,
                'day' : obj.day,
                'hour' : obj.hour,
                'minute' : obj.minute,
                'second' : obj.second,
                'microsecond' : obj.microsecond,
            }   
        else:
            return JSONEncoder.default(self, obj)

def get_value_from_key(key, dict):
    if key in dict:
        return dict[key]
    return ""

def get_name_from_tag(tag_list):
    for tag in tag_list:
        if tag["Key"] == "Name":
            return tag["Value"]
    return ""

def get_root_volume_id(instance_details):
    root_volume = get_value_from_key("RootDeviceName", instance_details)
    volume_list = get_value_from_key("BlockDeviceMappings", instance_details)
    for volume in volume_list:
        if volume["DeviceName"] == root_volume:
            return volume["Ebs"]["VolumeId"]
    return None

def get_id_name(profile="default", filter_running=False, region=None):
    botosession=boto3.session.Session(profile_name=profile, region_name=region)
    ec2=botosession.resource('ec2')

    id_name_map = {}

    client=botosession.client('ec2')
    if not filter_running:
        js = json.loads(json.dumps(client.describe_instances(Filters=[{"Name":"instance-state-name", "Values":["running"] }]),cls=DateTimeEncoder), cls=DateTimeDecoder)
    else:
        js = json.loads(json.dumps(client.describe_instances(),cls=DateTimeEncoder), cls=DateTimeDecoder)
    for reservation in js["Reservations"]:
        for instance in reservation["Instances"]:
            id_name_map[get_name_from_tag(get_value_from_key("Tags", instance))] = (get_value_from_key("InstanceId", instance),get_root_volume_id(instance))
    return id_name_map

def arguments_creation():
    parser = argparse.ArgumentParser(
         description='Make things happen.')
    parser.add_argument('-p', '--profile', default="default", help='Profile to use', required=False)
    parser.add_argument('-r', '--region', default=None, help='Region to override the default one')
    parser.add_argument('--stopped-vm', action='store_true', help="Show also stopped machine")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    arguments = arguments_creation()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(get_id_name(profile=arguments.profile, filter_running=arguments.stopped_vm, region=arguments.region))


