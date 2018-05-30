import json
import boto3
from datetime import datetime
from influxdb import InfluxDBClient

def lambda_handler(event, context):
    # There are better ways of controlling access but this will work for
    # the purposes of this example
    db_host = 'localhost'
    db_port = 8086
    db_user = 'root'
    db_pass = 'root'
    db_name = 'instance_counter'

    ec2 = boto3.resource('ec2')
    instances = list(ec2.instances.filter(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running'
                ]
            },
            {
                'Name': 'tag:Type',
                'Values': [
                    'Development',
                ]
            },
        ]
    ))
    num_instances = len(instances)

    # Now publish
    time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SGMT")
    json_body = [
    {
        "measurement": "ec2_instances",
        "tags": {
            "Type": "Development"
        },
        "time": time,
        "fields": {
            "value": num_instances
        }
    }
    ]
    client = InfluxDBClient(db_host, db_port, db_user, db_pass)
    dbs = client.get_list_database()
    if not [element for element in dbs if element['name'] == db_name]:
        client.create_database(db_name)
    out = client.write_points(json_body, None, db_name)
