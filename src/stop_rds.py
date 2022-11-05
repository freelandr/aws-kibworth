import boto3
import json
from datetime import datetime
import utils

rds = boto3.client('rds')

def lambda_handler(event, context):
    print('stop_rds: START')
    global rds
    
    print(event)    
    post_body = json.loads(event['body'])
    
    if not utils.is_password_valid(post_body['password']):
        response_code = 400
        response_body = {
            "message": "stop_rds: password is invalid",
            "RDS response": {},
        }        
    else:
        
        try:
            rds.describe_db_instances(DBInstanceIdentifier='kibworth')
            
            existingSnapshots = rds.describe_db_snapshots(DBInstanceIdentifier='kibworth')['DBSnapshots']
            snapshot_name = f'kibworth-snapshot-{str(int(datetime.utcnow().timestamp()))}'

            for snapshot in existingSnapshots:
                if 'kibworth-snapshot-' in snapshot['DBSnapshotIdentifier']:
                    print(f"stop_rds: deleting snapshot {snapshot['DBSnapshotIdentifier']}")
                    rds.delete_db_snapshot(DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier'])
            
            print(f'stop_rds: deleting database and creating final snapshot: {snapshot_name}')
            rds_response = rds.delete_db_instance(DBInstanceIdentifier='kibworth', FinalDBSnapshotIdentifier=snapshot_name, DeleteAutomatedBackups=True)
            update_security_group()
            
            response_code = 200
            response_body = {
                "message": "stop_rds: database shutting down",
                "RDS response": rds_response
            }
        except rds.exceptions.DBInstanceNotFoundFault:
            response_code = 400
            response_body = {
                "message": "stop_rds: kibworth database instance does not exist",
                "RDS response": {},
            }        
    
    response = {"statusCode": response_code, "body": json.dumps(response_body, indent=4, default = str)} 

    print(f'stop_rds: END - returning response: {response}')

    return response
    
def update_security_group():
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_security_groups(
        Filters=[
            dict(Name='group-name', Values=['kibworth-db-sg'])
        ]
    )    
    group_id = response['SecurityGroups'][0]['GroupId']
    
    print(f"update_security_group: found security group: {response['SecurityGroups'][0]}")
    
    for rule in response['SecurityGroups'][0]['IpPermissions']:
        for ip_range in rule['IpRanges']:
            if 'Client' in ip_range['Description']:
                print(f"update_security_group: revoking access for: {ip_range['Description']}")   
                ec2_client.revoke_security_group_ingress(
                    GroupId=group_id, 
                    CidrIp=ip_range['CidrIp'], 
                    IpProtocol='tcp', 
                    FromPort=5432, 
                    ToPort=5432
                )
    