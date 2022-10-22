import boto3
import json
from operator import itemgetter

rds = None

def lambda_handler(event, context):
    print('restore_rds: START')
    global rds
    rds = boto3.client('rds')
    
    if len(rds.describe_db_instances(DBInstanceIdentifier='kibworth')['DBInstances']) > 0:
        response_code = 400
        response_body = {
            "message": "restore_rds: unable to restore - kibworth database instance already exists",
            "RDS response": {},
        }
    else:
        rds_response = restore_latest_snapshot()
        response_code = 200
        response_body = {
            "message": "restore_rds: complete",
            "RDS response": rds_response,
        }  
    
    response = {"statusCode": response_code, "body": json.dumps(response_body, indent=4)}    
    
    print(f'restore_rds: END - returing response: {response}')
    
    return response        
   
def restore_latest_snapshot():
    global rds
    availableSnapshots=[]
    for snapshot in rds.describe_db_snapshots(DBInstanceIdentifier='kibworth')['DBSnapshots']:
        if snapshot['Status']=='available':
            availableSnapshots.append(snapshot['DBSnapshotIdentifier'])
    
    latestSnapshot = sorted(availableSnapshots, key=itemgetter('SnapshotCreateTime'), reverse=True)[0]
    
    print(f'restoring snapshot {latestSnapshot}')
    
    return rds.restore_db_instance_from_db_snapshot(
        DBInstanceIdentifier='kibworth',
        DBSnapshotIdentifier=latestSnapshot
    )