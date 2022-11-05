import boto3
import json
import utils
from operator import itemgetter

rds = boto3.client('rds')

def lambda_handler(event, context):
    print('restore_rds: START')
    global rds

    print(event)
    post_body = json.loads(event['body'])
    
    if not utils.is_password_valid(post_body['password']):
        response_code = 400
        response_body = {
            "message": "restore_rds: password is invalid",
            "RDS response": {},
        }        
    else:    

        try:
            rds.describe_db_instances(DBInstanceIdentifier='kibworth')
            response_code = 400
            response_body = {
                "message": "restore_rds: unable to restore - kibworth database instance already exists",
                "RDS response": {},
            }
        except rds.exceptions.DBInstanceNotFoundFault:
            rds_response = restore_latest_snapshot()
            update_security_group(event['headers']['x-forwarded-for'])
            response_code = 200
            response_body = {
                "message": "restore_rds: complete",
                "RDS response": rds_response,
            }  
    
    response = {"statusCode": response_code, "body": json.dumps(response_body, indent=4, default = str)}    
    
    print(f'restore_rds: END - returning response: {response}')
    
    return response        
   
def restore_latest_snapshot():
    global rds
    availableSnapshots=[]
    for snapshot in rds.describe_db_snapshots(DBInstanceIdentifier='kibworth')['DBSnapshots']:
        if snapshot['Status']=='available':
            availableSnapshots.append(snapshot)
    
    latestSnapshot = sorted(availableSnapshots, key=itemgetter('SnapshotCreateTime'), reverse=True)[0]
    
    print(f"restoring snapshot {latestSnapshot['DBSnapshotIdentifier']}")
    
    return rds.restore_db_instance_from_db_snapshot(
        DBInstanceIdentifier='kibworth',
        DBSnapshotIdentifier=latestSnapshot['DBSnapshotIdentifier']
    )
    
def update_security_group(sourceIP: str):
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_security_groups(
        Filters=[
            dict(Name='group-name', Values=['kibworth-db-sg'])
        ]
    )    
    group_id = response['SecurityGroups'][0]['GroupId']
    print(f"update_security_group: found security group: {response['SecurityGroups'][0]}")

    for rule in response['SecurityGroups'][0]['IpPermissions']:
        if sourceIP in rule['IpRanges'][0]['CidrIp']:
            print(f'update_security_group: traffic already allowed from {sourceIP}')
            return
    
    print(f'update_security_group: allowing traffic from {sourceIP}')
    
    ec2_client.authorize_security_group_ingress( 
    GroupId=group_id, 
    IpPermissions=[
        {
            'IpProtocol': 'tcp', 
            'FromPort': 5432,
            'ToPort': 5432, 
            'IpRanges': [{ 'CidrIp': f'{sourceIP}/32', 'Description': f'Client-{sourceIP}' }],
            'UserIdGroupPairs': [{ 'GroupId': group_id }] 
        }
    ],
    )
