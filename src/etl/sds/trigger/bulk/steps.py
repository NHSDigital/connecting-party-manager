from etl_utils.trigger.model import StateMachineInput
from event.step_chain import StepChain

from .operations import (
    start_execution,
    validate_database_is_empty,
    validate_no_changelog_number,
    validate_state_keys_are_empty,
)

Data = tuple[str, str, StateMachineInput]


def _validate_no_changelog_number(data, cache: dict):
    source_bucket, _, _ = data[StepChain.INIT]
    validate_no_changelog_number(
        s3_client=cache["s3_client"], source_bucket=source_bucket
    )


def _validate_state_keys_are_empty(data, cache: dict):
    source_bucket, _, _ = data[StepChain.INIT]
    validate_state_keys_are_empty(
        s3_client=cache["s3_client"], source_bucket=source_bucket
    )


def _validate_database_is_empty(data, cache: dict):
    validate_database_is_empty(
        dynamodb_client=cache["dynamodb_client"], table_name=cache["table_name"]
    )


def _copy_to_state_machine(data: dict[str, Data], cache):
    source_bucket, source_key, state_machine_input = data[StepChain.INIT]
    return cache["s3_client"].copy_object(
        Bucket=source_bucket,
        Key=state_machine_input.init,
        CopySource=f"{source_bucket}/{source_key}",
    )


def _copy_to_history(data: dict[str, Data], cache):
    source_bucket, source_key, _ = data[StepChain.INIT]
    return cache["s3_client"].copy_object(
        Bucket=source_bucket,
        Key=f"history/{source_key}",
        CopySource=f"{source_bucket}/{source_key}",
    )


def _delete_object(data: dict[str, Data], cache):
    source_bucket, source_key, _ = data[StepChain.INIT]
    return cache["s3_client"].delete_object(Bucket=source_bucket, Key=source_key)


def _start_execution(data: dict[str, Data], cache):
    _, _, state_machine_input = data[StepChain.INIT]
    return start_execution(
        step_functions_client=cache["step_functions_client"],
        state_machine_arn=cache["state_machine_arn"],
        state_machine_input=state_machine_input,
    )


steps = [
    _validate_no_changelog_number,
    _validate_state_keys_are_empty,
    _validate_database_is_empty,
    _copy_to_state_machine,
    _copy_to_history,
    _delete_object,
    _start_execution,
]
