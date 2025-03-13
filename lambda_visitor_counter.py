import boto3
import json


def lambda_handler(event, context):
    try:
        table_name, primary_key = get_inputs(event)
        visitor_counter = get_updated_visitor_counter(table_name, primary_key)
        
        return response_data(status_code=200, body={'visitorCount': visitor_counter})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return response_data(status_code=500, body={'error': str(e)})
    

def get_inputs(event):
    body = json.loads(event['body'])
    return body['tableName'], body['primaryKey']


def get_updated_visitor_counter(table_name, primary_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    # Atomically increment visitorCount by 1.
    response = table.update_item(
        Key={primary_key: 'counter'},
        UpdateExpression="SET visitorCount = if_not_exists(visitorCount, :start) + :incr",
        ExpressionAttributeValues={
            ':incr': 1,
            ':start': 0
        },
        ReturnValues="UPDATED_NEW"
    )
    updated_count = response['Attributes']['visitorCount']
    return int(updated_count)


def response_data(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }
