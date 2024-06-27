import json
from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from etl_utils.trigger.model import StateMachineInputType, TriggerResponse

if TYPE_CHECKING:
    from mypy_boto3_lambda import LambdaClient


def notify(
    lambda_client: "LambdaClient",
    function_name: str,
    result: Exception | Any,
    trigger_type: StateMachineInputType,
):
    status = "Unsuccessful" if isinstance(result, Exception) else "Successful"
    trigger_response = TriggerResponse(
        message=f"{status} '{trigger_type}' trigger of state machine.",
        error_message=str(result) if isinstance(result, Exception) else None,
    )
    response = lambda_client.invoke(
        FunctionName=function_name,
        Payload=json.dumps([asdict(trigger_response)]).encode(),
    )
    return response["Payload"].read()
