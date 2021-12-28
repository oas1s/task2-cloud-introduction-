import requests

def handler(event, context):
    r = requests.get('http://94.180.150.200:8081')
    return {
        'statusCode': 200,
        'body': 'Hello World!',
    }
