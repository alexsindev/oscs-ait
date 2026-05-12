import boto3
import requests
from decimal import Decimal
from boto3.dynamodb.types import TypeSerializer

def _to_dynamo_value(value):
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: _to_dynamo_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_dynamo_value(v) for v in value]
    return value

def to_dynamo_item(obj):
    return {k: TypeSerializer().serialize(_to_dynamo_value(v)) for k, v in obj.items()}

def get_response():
    ec2_ip = "35.175.222.203"
    url = f"http://{ec2_ip}/api/telemetry"
    response = requests.get(url, timeout=10)
    return response.json()

def send_to_dynamodb(events):
    dynamodb_table_name = "st126112-dynamodb-15032026"
    if not events:
        return 0
    dynamodb = boto3.client("dynamodb")
    count = 0
    for event in events:
        item = to_dynamo_item(event)
        dynamodb.put_item(TableName=dynamodb_table_name, Item=item)
        count += 1
    return count

def lambda_handler(event, context):
    if event.get("records") is not None:
        events = event["records"]
    else:
        try:
            events = get_response()
        except Exception as exc:
            return {
                "statusCode": 500,
                "body": f"Failed to fetch events: {exc}",
            }

    count = send_to_dynamodb(events)

    return {
        "statusCode": 200,
        "body": f"Successfully ingested {count} events into DynamoDB table",
    }