import json
from typing import TYPE_CHECKING, Any

from etl_utils.trigger.model import StateMachineInputType

if TYPE_CHECKING:
    from mypy_boto3_lambda import LambdaClient


def notify(
    lambda_client: "LambdaClient",
    function_name: str,
    result: Exception | Any,
    trigger_type: StateMachineInputType,
):
    status = "Unsuccessful" if isinstance(result, Exception) else "Successful"
    error_message = str(result) if isinstance(result, Exception) else None
    response = lambda_client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(
            {
                "message": f"{status} '{trigger_type}' trigger of state machine.",
                "error_message": error_message,
            }
        ).encode(),
    )
    return response["Payload"].read()
