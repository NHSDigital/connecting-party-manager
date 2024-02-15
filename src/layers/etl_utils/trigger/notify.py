import json
from typing import Any


def notify(
    lambda_client,
    function_name: str,
    result: Exception | Any,
    state_machine_name: str,
):
    status = "Unsuccessful" if isinstance(result, Exception) else "Successful"
    error_message = str(result) if isinstance(result, Exception) else None
    response = lambda_client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(
            {
                "message": f"{status} trigger of state machine {state_machine_name}",
                "error_message": error_message,
            }
        ).encode(),
    )
    return response["Payload"].read()
