import base64
import gzip
import http.client
import json
import os

import boto3

# Replace with your Dynatrace API token and URL
DYNATRACE_API_TOKEN = os.environ.get('DT_LOG_COLLECTION_AUTH_TOKEN')
DYNATRACE_URL = 'ktv92122.live.dynatrace.com'

def send_log_to_dynatrace(log_data):
    # Your existing code for sending logs to Dynatrace
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

def extract_log_message(event):
    # Your logic to extract the log message from the CloudWatch event
    # Modify this part based on the structure of your CloudWatch event
    return event.get('logMessage', 'UnknownLogMessage')

def lambda_handler(event, context):
    # Print the entire event for debugging
    print("Received event:", json.dumps(event, indent=2))

    try:
        # Check if the event is triggered by a CloudWatch Alarm
        if 'source' in event and event['source'] == 'aws.cloudwatch':
            # Check if 'detail' key is present
            if 'detail' in event:
                # Extract log message from CloudWatch event
                log_message = extract_log_message(event)

                # Access relevant information from the CloudWatch Alarm event
                alarm_name = event['detail'].get('alarmName', 'UnknownAlarm')
                region = event['region']
                timestamp = event['time']

                # Create a log message specific to the CloudWatch Alarm event
                full_log_message = f"CloudWatch Alarm '{alarm_name}' triggered in region '{region}' at {timestamp}. Log Message: {log_message}"

                try:
                    # Send the log message to Dynatrace
                    send_log_to_dynatrace(full_log_message)

                except Exception as e:
                    # Handle exceptions
                    error_message = f"Error handling CloudWatch Alarm event: {str(e)}"
                    print(error_message)

                    # Send an error log to Dynatrace
                    send_log_to_dynatrace(error_message)
            else:
                print("No 'detail' key found in the CloudWatch Alarm event.")
        else:
            print("Event is not triggered by CloudWatch Alarm.")
    except KeyError as key_error:
        print(f"KeyError: {key_error}. Check the structure of the received event.")
    except Exception as general_error:
        print(f"Error handling event: {str(general_error)}")

# Uncomment the line below for local testing
# lambda_handler({"source": "aws.cloudwatch", "detail": {"state": "ALARM", "alarmName": "YourAlarmName", "logMessage": "YourLogMessage"}, "region": "your-region", "time": "timestamp"}, None)
