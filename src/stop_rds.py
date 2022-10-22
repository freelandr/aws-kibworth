import boto3

def lambda_handler(event, context):
    print('stop_rds: START')
    rds = boto3.client('rds')
    response = {"statusCode": 200}
    return response