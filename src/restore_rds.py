import boto3
import json

def lambda_handler(event, context):
    print('restore_rds: START')
    
    rds = boto3.client('rds')
    availableSnapshots=[]
    for snapshot in rds.describe_db_snapshots(DBInstanceIdentifier='kibworth', 
                                                SnapshotType='automated')['DBSnapshots']:
        if snapshot['Status']=='available':
            availableSnapshots.append(snapshot['DBSnapshotIdentifier'])
    
    latestSnapshot = sorted(id, reverse=True)[0]
    
    print(f'restoring snapshot {latestSnapshot}')
    
    rds_response = rds.restore_db_instance_from_db_snapshot(
        DBInstanceIdentifier='kibworth',
        DBSnapshotIdentifier=latestSnapshot
    )
    
    response_body = {
        "message": "restore_rds complete",
        "RDS response": rds_response,
    }    
    
    response = {"statusCode": 200, "body": json.dumps(response_body)}    
    
    return response