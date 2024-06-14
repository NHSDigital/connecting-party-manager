from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from etl_utils.constants import WorkerKey
from etl_utils.trigger.model import StateMachineInput
from etl_utils.trigger.operations import start_execution, validate_state_keys_are_empty
from event.step_chain import StepChain

from .operations import validate_database_is_empty, validate_no_changelog_number

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_stepfunctions import SFNClient


class Cache(TypedDict):
    s3_client: "S3Client"
    step_functions_client: "SFNClient"
    dynamodb_client: "DynamoDBClient"
    state_machine_arn: str
    table_name: str


def _validate_no_changelog_number(data, cache: Cache):
    source_bucket, _ = data[StepChain.INIT]
    validate_no_changelog_number(
        s3_client=cache["s3_client"], source_bucket=source_bucket
    )


def _validate_state_keys_are_empty(data, cache: Cache):
    source_bucket, _ = data[StepChain.INIT]
    validate_state_keys_are_empty(s3_client=cache["s3_client"], bucket=source_bucket)


def _validate_database_is_empty(data, cache: Cache):
    validate_database_is_empty(
        dynamodb_client=cache["dynamodb_client"], table_name=cache["table_name"]
    )


def _create_state_machine_input(data, cache):
    _, source_key = data[StepChain.INIT]
    return StateMachineInput.bulk(changelog_number=Path(source_key).stem)


def _copy_to_state_machine(data, cache: Cache):
    source_bucket, source_key = data[StepChain.INIT]
    return cache["s3_client"].copy_object(
        Bucket=source_bucket,
        Key=WorkerKey.EXTRACT,
        CopySource=f"{source_bucket}/{source_key}",
    )


def _copy_to_history(data, cache: Cache):
    source_bucket, source_key = data[StepChain.INIT]
    state_machine_input: StateMachineInput = data[_create_state_machine_input]
    return cache["s3_client"].copy_object(
        Bucket=source_bucket,
        Key=f"history/{state_machine_input.etl_type}/{source_key}",
        CopySource=f"{source_bucket}/{source_key}",
    )


def _delete_object(data, cache: Cache):
    source_bucket, source_key = data[StepChain.INIT]
    return cache["s3_client"].delete_object(Bucket=source_bucket, Key=source_key)


def _start_execution(data, cache):
    state_machine_input: StateMachineInput = data[_create_state_machine_input]
    return start_execution(
        step_functions_client=cache["step_functions_client"],
        state_machine_arn=cache["state_machine_arn"],
        state_machine_input=state_machine_input,
    )


steps = [
    _validate_no_changelog_number,
    _validate_state_keys_are_empty,
    _validate_database_is_empty,
    _create_state_machine_input,
    _copy_to_state_machine,
    _copy_to_history,
    _delete_object,
    _start_execution,
]
