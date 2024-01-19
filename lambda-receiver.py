import base64
import http.client
import json
import os
import zlib

import boto3

# Replace with your Dynatrace API token and URL
DYNATRACE_API_TOKEN = os.environ.get('DT_LOG_COLLECTION_AUTH_TOKEN')
DYNATRACE_URL = 'cut57585.live.dynatrace.com'

def send_log_to_dynatrace(log_data):
    conn = http.client.HTTPSConnection(DYNATRACE_URL)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Token {DYNATRACE_API_TOKEN}',
    }

    payload = {
        'lines': [
            {'log': log_data}
        ]
    }

    json_payload = json.dumps(payload)

    conn.request('POST', '/api/v2/logs/ingest', json_payload, headers)
    response = conn.getresponse()

    if response.status != 200:
        print(f"Failed to send log to Dynatrace. Status Code: {response.status}, Response: {response.read().decode()}")
    else:
        print("Log sent to Dynatrace successfully.")

    conn.close()

def lambda_handler(event, context):
    # Retrieve the request ID from the context
    request_id = context.aws_request_id

    # Extract the payload from the event
    awslogs_data = event.get('awslogs', {}).get('data', '')
    
    try:
        # Log the raw Base64-encoded payload
        print(f"Raw Base64-encoded payload (Request ID: {request_id}):", awslogs_data)

        # Decode the Base64-encoded payload
        decoded_data = base64.b64decode(awslogs_data)
        
        # Decompress the data using zlib
        uncompressed_data = zlib.decompress(decoded_data, 16+zlib.MAX_WBITS)
        
        # Print the payload received from the invoking Lambda function along with the request ID
        received_payload = uncompressed_data.decode('utf-8')
        print(f"Received payload (Request ID: {request_id}):", received_payload)

        # Send the log to Dynatrace
        send_log_to_dynatrace(received_payload)

    except zlib.error as e:
        # Handle decompression errors
        error_message = f"Error decoding/decoding payload (Request ID: {request_id}): {str(e)}"
        print(error_message)

        # Send the error log to Dynatrace
        send_log_to_dynatrace(error_message)

    # Process the payload or perform other tasks
    if 'key1' in event and 'key2' in event and 'key3' in event:
        value1 = event['key1']
        value2 = event['key2']
        value3 = event['key3']

        # Example: Perform some processing using the values
        result = value1 + ' ' + value2 + ' ' + value3

        # Example: Log the result along with the request ID
        processed_result = f"Processed result (Request ID: {request_id}): {result}"
        print(processed_result)

        # Send the processed result log to Dynatrace
        send_log_to_dynatrace(processed_result)

        # Example: Send the result to another Lambda function
        invokeLam = boto3.client("lambda", region_name="us-east-1")
        payload = {"result": result}
        resp = invokeLam.invoke(FunctionName="lamda-invoke", InvocationType="Event", Payload=json.dumps(payload))
        print("Result sent for further processing.")

    return 'Thanks'


