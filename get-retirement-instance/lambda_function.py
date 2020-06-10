import json
import boto3
import sys


try:
    ec2_client = boto3.client('ec2')
except Exception as e:
    print("ERROR: failed to connect to EC2")
    sys.exit(1)

def update_retirement_tag(resources):
    try:
        ec2_client.create_tags(
            Resources = resources,
            Tags = [
                {
                    'Key': 'retirement_scheduled',
                    'Value': 'scheduled'
                }
            ]
        )
    except Exception as e:
        print("ERROR: failed to add tags to EC2")
        print(e)
        sys.exit(1)
    

def lambda_handler(event, context):
    # TODO implement
    
    eventTypeCode = event['detail']['eventTypeCode']
    if eventTypeCode == 'AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED':
        resources = event['resources']
        update_retirement_tag(resources)

    return {
        'statusCode': 200,
        'body': json.dumps('SUCCESSED: retirement instance scheduled')
    }
