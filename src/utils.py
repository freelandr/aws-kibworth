import boto3
import base64
import json

SECRET_NAME='kibworth_api_passwd'

def is_password_valid(password: str) -> bool:
    client = boto3.client('secretsmanager')
    
    get_secret_value_response = client.get_secret_value(SecretId=SECRET_NAME)
    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
    else:
        secret = base64.b64decode(get_secret_value_response['SecretBinary'])
    
    return password == json.loads(secret)['passwd']