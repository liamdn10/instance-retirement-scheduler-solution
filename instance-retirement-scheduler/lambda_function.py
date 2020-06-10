import json
import boto3
import sys
import os


try:
    ec2_client = boto3.client('ec2')
except Exception as e:
    print("ERROR: failed to connect to EC2")
    error_notification(e)
    sys.exit(1)
    
try:
    sns_client = boto3.client('sns')
except Exception as e:
    print("ERROR: failed to connect to SNS")
    error_notification(e)
    sys.exit(1)
    
SNS_TOPIC_ARN = os.environ.get('sns_topic_arn')

def get_instance_state(instance_id):
    
    # 0 : pending
    # 16 : running
    # 32 : shutting-down
    # 48 : terminated
    # 64 : stopping
    # 80 : stopped
    
    res = ec2_client.describe_instances(
        InstanceIds = [instance_id]
    )
    
    for reservation in res['Reservations']:
        for instance in reservation['Instances']:
            print(instance['State']['Code'])
            return(instance['State']['Code'])

def before_retirement():
    instances = []
    
    res = ec2_client.describe_instances(
        Filters = [
            {
                'Name': 'tag:retirement_scheduled',
                'Values': [
                    "scheduled"
                ]
            }
        ]
    )
    
    for reservation in res['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Code'] == 16:
                instances.append(instance['InstanceId'])
            else:
                after_retirement(instance['InstanceId'], 'canceled')
            
    return instances
    
def retirement(instances):
    try:
        ec2_client.stop_instances(
            InstanceIds = instances
        )
    except Exception as e:
        print("ERROR: failed to stop EC2 instances")
        print(e)
        error_notification(e)

    while len(instances) != 0:
        
        for instance in instances:
            state = get_instance_state(instance)
            if state == 16:
                after_retirement(instance, 'unknow')
                instances.remove(instance)
            elif state == 80:
                try:
                    ec2_client.start_instances(
                        InstanceIds = [instance]
                    )
                except Exception as e:
                    print("ERROR: failed to start EC2 instances " + instance)
                    print(e)
                    error_notification(e)
                    after_retirement(instance, 'failed')
                    instances.remove(instance)
                    
                after_retirement(instance, 'successed')
                instances.remove(instance)
    
def after_retirement(instance_id, status:str):
    resources = [instance_id]
    try:
        ec2_client.create_tags(
            Resources = resources,
            Tags = [
                {
                    'Key': 'retirement_scheduled',
                    'Value': status
                }
            ]
        )
    except Exception as e:
        print("ERROR: failed to add tags to EC2")
        print(e)
        error_notification(e)
        sys.exit(1)

def error_notification(e):
    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=str(e),
        Subject='Instance retirement scheduler'
    )
    
def lambda_handler(event, context):
    # TODO implement
    
    instances = before_retirement()
    print(instances)
    if len(instances) == 0:
        return {
        'statusCode': 200,
        'body': json.dumps('there is no instance retirement scheduled')
        }
    else: 
        retirement(instances)
    
    return {
        'statusCode': 200,
        'body': json.dumps('instance retirement scheduled successed')
    }
