#!/usr/bin/env python

import argparse
import boto3
import json
from json import JSONDecoder
from json import JSONEncoder
from datetime import datetime

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

def arguments_creation():
    parser = argparse.ArgumentParser(
         description='Make things happen.')
    parser.add_argument('-p', '--profile', default="default", help='Profile to use', required=False)
    args = parser.parse_args()
    return args

def main(profile="default"):
        #js = json.loads(open("/tmp/prova.json", "r").read())
    botosession=boto3.session.Session(profile_name=profile)
    #ec2=botosession.resource('rds')

    client=botosession.client('rds')
    #js = json.loads(client.describe_instances(), object_hook=json_serial)
    js = json.loads(json.dumps(client.describe_db_instances(), cls=DateTimeEncoder), cls=DateTimeDecoder)
    for db in js["DBInstances"]:
        print get_value_from_key("DBInstanceIdentifier", db) + "\t" + str(get_value_from_key("VpcSecurityGroups", db))


if __name__ == '__main__':
    arguments = arguments_creation()
    main(arguments.profile)