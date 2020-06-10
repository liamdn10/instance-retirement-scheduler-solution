# instance-retirement-scheduler
aws solution to scheduling instance retirement by your own event on your maintenance windows, instead of waiting for AWS scheduling

## Solution meaning
An instance is scheduled to be retired when AWS detects irreparable failure of the underlying hardware hosting the instance. When an instance reaches its scheduled retirement date, it is stopped or terminated by AWS. If your instance root device is an Amazon EBS volume, the instance is stopped, and you can start it again at any time. Starting the stopped instance migrates it to new hardware. If your instance root device is an instance store volume, the instance is terminated, and cannot be used again.</br>

If instance is running on your production environment, you need to start the instance quickly to minimize downtime. This solution provide a way to handle the retirement event by specifying a maintenance time to initiative stop and start instance, instead of doing manualy.</br>

*Ref: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-retirement.html*
## How it works
#### Step 1: Get event and tag the instance
<p align="center"><img src="https://user-images.githubusercontent.com/38157237/84226096-10056380-ab0b-11ea-8b69-3fbdfcf730e2.png"/></p>

#### Step 2: Stop/Start instance

## Deploy the solution
#### Prerequisites
#### Resources are created by CloudFormation template
#### Parameters
