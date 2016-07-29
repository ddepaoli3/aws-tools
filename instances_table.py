#!/usr/bin/env python

import json
import sys
import boto3
from datetime import datetime
from json import JSONDecoder
from json import JSONEncoder
import argparse

def arguments_creation():
    parser = argparse.ArgumentParser(
         description='Make things happen.')
    parser.add_argument('-p', '--profile', default="default", help='Profile to use', required=False)
    parser.add_argument('-o', '--output', default="weblike", help='Profile to use as output', choices=['weblike','securitygroup'], required=False)
    parser.add_argument('-r', '--region', default=None, help='Region to override the default one')
    parser.add_argument('--stopped-vm', action='store_true', help="Show also stopped machine")
    args = parser.parse_args()
    return args

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

def main_like_web_interface(profile="default", filter_running=False, region=None):
    #js = json.loads(open("/tmp/prova.json", "r").read())
    botosession=boto3.session.Session(profile_name=profile, region_name=region)
    ec2=botosession.resource('ec2')

    client=botosession.client('ec2')
    #js = json.loads(client.describe_instances(), object_hook=json_serial)
    if not filter_running:
        js = json.loads(json.dumps(client.describe_instances(Filters=[{"Name":"instance-state-name", "Values":["running"] }]),cls=DateTimeEncoder), cls=DateTimeDecoder)
    else:
        js = json.loads(json.dumps(client.describe_instances(),cls=DateTimeEncoder), cls=DateTimeDecoder)
    for reservation in js["Reservations"]:
        for instance in reservation["Instances"]:
            print get_name_from_tag(get_value_from_key("Tags", instance)) + "\t" + \
            get_value_from_key("InstanceId", instance) + "\t" + \
            get_value_from_key("InstanceType", instance) + "\t" + \
            get_value_from_key("Name", instance["State"]) + "\t" + \
            get_value_from_key("PublicIpAddress", instance) + "\t" + \
            get_value_from_key("PrivateIpAddress", instance) + "\t" + \
            get_value_from_key("KeyName", instance)

def main_security_group(profile="default", region=None):
        #js = json.loads(open("/tmp/prova.json", "r").read())
    botosession=boto3.session.Session(profile_name=profile, region_name=region)
    ec2=botosession.resource('ec2')

    client=botosession.client('ec2')
    #js = json.loads(client.describe_instances(), object_hook=json_serial)
    js = json.loads(json.dumps(client.describe_instances(),cls=DateTimeEncoder), cls=DateTimeDecoder)
    for reservation in js["Reservations"]:
        for instance in reservation["Instances"]:
            print get_name_from_tag(get_value_from_key("Tags", instance)) + "\t" + \
            get_value_from_key("InstanceId", instance) + "\t" + \
            str(get_value_from_key("SecurityGroups", instance))

if __name__ == '__main__':
    arguments = arguments_creation()
    if arguments.output == "securitygroup":
        main_security_group(arguments.profile)
    elif arguments.output == "weblike":
        main_like_web_interface(profile=arguments.profile, filter_running=arguments.stopped_vm, region=arguments.region)


