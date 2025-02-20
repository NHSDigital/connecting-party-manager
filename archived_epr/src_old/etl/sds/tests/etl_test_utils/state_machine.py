import json
from typing import TYPE_CHECKING

from etl_utils.trigger.model import StateMachineInput
from event.json import json_loads
from mypy_boto3_stepfunctions.type_defs import StartSyncExecutionOutputTypeDef

from test_helpers.terraform import read_terraform_output

if TYPE_CHECKING:
    from mypy_boto3_stepfunctions import SFNClient


def execute_state_machine(
    state_machine_input: StateMachineInput, step_functions_client: "SFNClient"
) -> StartSyncExecutionOutputTypeDef:
    state_machine_arn = read_terraform_output("sds_etl.value.state_machine_arn")
    name = state_machine_input.name
    execution_response = step_functions_client.start_execution(
        stateMachineArn=state_machine_arn,
        name=name,
        input=json.dumps(state_machine_input.dict()),
    )

    status = "RUNNING"
    while status == "RUNNING":
        response = step_functions_client.describe_execution(
            executionArn=execution_response["executionArn"]
        )
        status = response["status"]

    if response["status"] != "SUCCEEDED":
        try:
            cause = json_loads(response["cause"])
            error_message = cause["errorMessage"]
            stack_trace = cause["stackTrace"]
        except Exception:
            error_message = response.get("cause", "no error message")
            stack_trace = []

        print(  # noqa: T201
            "Error captured from state machine:\n",
            error_message,
            "\n",
            *stack_trace,
        )
        raise RuntimeError(response.get("error", "no error message"))
    print("state machine response:", response)  # noqa
    return response
