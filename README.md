# instance-retirement-scheduler
aws solution to scheduling instance retirement by your own event on your maintenance windows, instead of waiting for AWS scheduling

## Solution meaning
An instance is scheduled to be retired when AWS detects irreparable failure of the underlying hardware hosting the instance. When an instance reaches its scheduled retirement date, it is stopped or terminated by AWS. If your instance root device is an Amazon EBS volume, the instance is stopped, and you can start it again at any time. Starting the stopped instance migrates it to new hardware. If your instance root device is an instance store volume, the instance is terminated, and cannot be used again.</br>

If instance is running on your production environment, you need to start the instance quickly to minimize downtime. This solution provide a way to handle the retirement event by specifying a maintenance time to initiative stop and start instance, instead of doing manualy.</br>

*Ref: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-retirement.html*
## How it works
#### Step 1: Get event and tag the instance
<p align="center"><img src="https://user-images.githubusercontent.com/38157237/84226096-10056380-ab0b-11ea-8b69-3fbdfcf730e2.png"/></p>

Cloudwatch rules provide system health event. The event for instance retirement trigger to a lambda function, get the **resources** list from event, then add the tag key **retirement_scheduled** with value **scheduled**. The json below is an example of an instance retirement event:
```json
{
  "version": "0",
  "id": "7bf73129-1428-4cd3-a780-95db273d1602",
  "detail-type": "AWS Health Event",
  "source": "aws.health",
  "account": "123456789012",
  "time": "2016-06-05T06:27:57Z",
  "region": "us-west-2",
  "resources": [
    "i-08f112b7715098572"
  ],
  "detail": {
    "eventArn": "arn:aws:health:us-west-2::event/AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED_90353408594353980",
    "service": "EC2",
    "eventTypeCode": "AWS_EC2_INSTANCE_RETIREMENT_SCHEDULED",
    "eventTypeCategory": "scheduleChanged",
    "startTime": "Sat, 05 Jun 2016 15:10:09 GMT",
    "eventDescription": [
      {
        "language": "en_US",
        "latestDescription": "A description of the event will be provided here"
      }
    ],
    "affectedEntities": [
      {
        "entityValue": "i-08f112b7715098572",
        "tags": {
          "stage": "prod",
          "app": "my-app"
        }
      }
    ]
  }
}
```

#### Step 2: Stop/Start instance
<p align="center"><img src="https://user-images.githubusercontent.com/38157237/84231698-e8b59300-ab18-11ea-960a-1a34a8da5711.png"/></p>

On a day of week, a CloudWatch event schedule trigger a lambda function to get the list of instance need to be retired by a tag filter
```python
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
```
Then, lambda function will stop instances, and restart after instances state return to stopped
## Deploy the solution

#### Prerequisites
- You need to create a SNS topic for notification
- Your account should have enough permissions to create resources

#### Resources are created by CloudFormation template
The template will create the resources below:
- 1 schedule rule
- 1 event rule
- 2 lambda invoke permission
- 2 lambda function
- 2 role for lambda function
- 2 policy for role for lambda function

#### Parameters

| Parameter | Default | Description |
|---|---|---|
|ProjectPrefix||Project prefix for creating resource name like ${ProjectPrefix}-resourceName|
|SnsTopic||SNS topic arn for notification|
|State|ENABLED|State of solution ENALBLED/DISABLED|
|MaintenanceHour|17|Time at hour to start retirement schedule by GMT TimeZone|
|MaintenanceMinute|0|Time at minute of MaintenanceHour to start retirement schedule by GMT TimeZone|
|MaintenanceDayOfWeek|SAT|Day in week to start retirement schedule by GMT TimeZone|

#### Note
- You can create an alarm for notification if an error occured to your lambda function
- If lambda sources stored in S3, rename the S3Bucket and S3Key to your sources.
