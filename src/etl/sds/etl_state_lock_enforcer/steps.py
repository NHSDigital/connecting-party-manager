from typing import TYPE_CHECKING, TypedDict

from etl_utils.constants import (
    ETL_QUEUE_HISTORY,
    ETL_STATE_LOCK,
    ETL_STATE_MACHINE_HISTORY,
    WorkerKey,
)
from etl_utils.trigger.model import StateMachineInput
from etl_utils.trigger.operations import start_execution, validate_state_keys_are_empty
from event.json import json_loads
from event.step_chain import StepChain

from .operations import etl_state_lock_doesnt_exist_in_s3

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_stepfunctions import SFNClient


class StateLockExistsError(Exception):
    """Custom exception for existing ETL state lock."""

    pass


class Cache(TypedDict):
    s3_client: "S3Client"
    step_functions_client: "SFNClient"
    state_machine_arn: str
    etl_bucket: str
    etl_extract_input_key: str


def _process_sqs_message(data, cache: Cache):
    message = data[StepChain.INIT]
    body = json_loads(message["body"])
    state_machine_name = body["name"]

    # Validate and create StateMachineInput instance
    state_machine_input = StateMachineInput(**body)

    return state_machine_input, state_machine_name


def _check_etl_lock(data, cache: Cache):
    _, state_machine_name = data[_process_sqs_message]

    s3_client = cache["s3_client"]
    etl_bucket = cache["etl_bucket"]

    if etl_state_lock_doesnt_exist_in_s3(s3_client=s3_client, bucket=etl_bucket):
        # Aquire state lock
        return s3_client.put_object(
            Bucket=cache["etl_bucket"],
            Key=ETL_STATE_LOCK,
            Body=state_machine_name,
        )

    else:
        raise StateLockExistsError("ETL state lock already exists.")


def _validate_state_keys_are_empty(data, cache: Cache):
    return validate_state_keys_are_empty(
        s3_client=cache["s3_client"], bucket=cache["etl_bucket"]
    )


def _put_to_state_machine(data, cache: Cache):
    _, state_machine_name = data[_process_sqs_message]
    s3_client = cache["s3_client"]
    etl_bucket = cache["etl_bucket"]

    # Update state machine history file
    s3_client.copy_object(
        Bucket=cache["etl_bucket"],
        Key=f"{ETL_STATE_MACHINE_HISTORY}/{state_machine_name}",
        CopySource=f'{cache["etl_bucket"]}/{ETL_QUEUE_HISTORY}/{state_machine_name}',
    )

    return s3_client.copy_object(
        Bucket=etl_bucket,
        Key=WorkerKey.EXTRACT,
        CopySource=f'{cache["etl_bucket"]}/etl_state_machine_history/{state_machine_name}',
    )


def _start_execution(data, cache):
    state_machine_input, state_machine_name = data[_process_sqs_message]
    return start_execution(
        step_functions_client=cache["step_functions_client"],
        state_machine_arn=cache["state_machine_arn"],
        state_machine_input=state_machine_input,
        state_machine_name=state_machine_name,
    )


steps = [
    _process_sqs_message,
    _check_etl_lock,
    _validate_state_keys_are_empty,
    _put_to_state_machine,
    _start_execution,
]
