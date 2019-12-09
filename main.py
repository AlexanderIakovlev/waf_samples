import boto3, os
from datetime import datetime, timedelta, timezone

# Need this for combine name as we do in terraform
# Put your project and environment here

project = ''
environment = ''

# Assume that use default provider in ~/.aws/credentials
# If not please use AWS_PROFILE environment variable for pointing into valid AWS account
# Example:
#
#if environment == 'stage':
#    os.environ['AWS_PROFILE'] = 'prod'
#else:
#    os.environ['AWS_PROFILE'] = 'dev'

# Create client to connect AWS service
waf_regional = boto3.client('waf-regional')
#waf = boto3.client('waf')

# Get WAF ACL ID for our project
responses = waf_regional.list_web_acls()
for response in responses['WebACLs']:
    if response['Name'] == project + '-' + environment + '-global-WAF':
        webalcid = response['WebACLId']

# Get WAF Rule ID for our project
responses = waf_regional.list_rules()
for response in responses['Rules']:
    if response['Name'] == project + '-' + environment + '-global-detect-blacklisted-ips':
        ruleid = response['RuleId']

item_num = 100
# 1 hour
interval_time = 60

# Using datetime to create the start&end time for 'waf.get_sampled_requests()'
# if necessary you can modify timedelta() to get time window size u want
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(minutes=interval_time)

# Get sample log from aws waf
waf_response = waf_regional.get_sampled_requests(
    WebAclId=webalcid,
    RuleId=ruleid,
    TimeWindow={
        'StartTime': start_time,
        'EndTime': end_time
    },
    MaxItems= item_num
)

for output in waf_response['SampledRequests']:
    #print(output)
    print(output['Request']['ClientIP'] + " " + output['Request']['URI'] + " " + output['Request']['Method'] + " " + str(output['Request']['Headers']))


    #digital ocean
    #if output['Request']['ClientIP'] == '167.71.135.207':
    #    print(output['Request'])

    #salesforce
    # for header in output['Request']['Headers']:
    #     if header['Name'] == 'User-Agent':
    #         if header['Value'] == 'SFDC-Callout/47.0':
    #             print(output['Request']['ClientIP'])
