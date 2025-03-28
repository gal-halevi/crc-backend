import boto3
import json


def lambda_handler(event, context):
    """
    AWS Lambda function to handle visitor counter updates.
    This function retrieves the table name and primary key from the event input,
    updates the visitor counter in the specified DynamoDB table, and returns
    the updated visitor count in the response. If an error occurs, it logs the
    traceback and returns an error response.
    Args:
        event (dict): The event data passed to the Lambda function, typically
                      containing input parameters such as table name and primary key.
        context (object): The runtime information provided by AWS Lambda.
    Returns:
        dict: A response object containing the HTTP status code and body.
              On success, the body contains the updated visitor count.
              On failure, the body contains an error message.
    """
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
    """
    Updates and retrieves the visitor counter from a DynamoDB table.

    This function connects to a DynamoDB table, atomically increments the 
    `visitorCount` attribute by 1, and returns the updated count. If the 
    `visitorCount` attribute does not exist, it initializes it to 0 before 
    incrementing.

    Args:
        table_name (str): The name of the DynamoDB table.
        primary_key (str): The name of the primary key attribute in the table.

    Returns:
        int: The updated visitor count after the increment.

    Raises:
        botocore.exceptions.ClientError: If there is an error with the DynamoDB operation.
    """
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
