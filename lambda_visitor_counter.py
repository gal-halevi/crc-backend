import boto3
import json


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        table_name = body['tableName']
        primary_key = body['primaryKey']
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
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'visitorCount': int(updated_count)})
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
