def lambda_handler(event, context):
    try:
        # Your main logic here 
        payload = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
        print(payload)
        # Check for any error conditions and raise an exception if needed 
        if some_error_condition: 
            return Exception("An error occurred")
        # If everything is successful, return the payload along with a success message
        response = {'status': 'success', 'payload': payload}
        return response
    except Exception as e:
        # If an exception occurs, return an error message
        error_response = {'status': 'error', 'error_message': str(e)}
        print(error_response)  # Log the error for visibility
        return error_response
        
    