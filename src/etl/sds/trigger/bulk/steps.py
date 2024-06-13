import json
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

import boto3
from etl_utils.trigger.model import StateMachineInput
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
    etl_bucket: str


def _validate_no_changelog_number(data, cache: Cache):
    source_bucket, _ = data[StepChain.INIT]
    validate_no_changelog_number(
        s3_client=cache["s3_client"], source_bucket=source_bucket
    )


def _validate_database_is_empty(data, cache: Cache):
    validate_database_is_empty(
        dynamodb_client=cache["dynamodb_client"], table_name=cache["table_name"]
    )


def _create_state_machine_input(data, cache):
    _, source_key = data[StepChain.INIT]
    state_machine_input = StateMachineInput.bulk(changelog_number=Path(source_key).stem)
    return state_machine_input


def _copy_to_intermediate_history_file(data, cache: Cache):
    source_bucket, source_key = data[StepChain.INIT]
    state_machine_input: StateMachineInput = data[_create_state_machine_input]
    return cache["s3_client"].copy_object(
        Bucket=source_bucket,
        Key=f"history/{state_machine_input.name}",
        CopySource=f"{source_bucket}/{source_key}",
    )


def _delete_trigger_object(data, cache: Cache):
    source_bucket, source_key = data[StepChain.INIT]
    return cache["s3_client"].delete_object(Bucket=source_bucket, Key=source_key)


def _publish_message_to_sqs_queue(data, cache: Cache):
    sqs_client = boto3.client("sqs")

    # Convert the state_machine_input to JSON
    state_machine_input: StateMachineInput = data[_create_state_machine_input]
    state_machine_name = state_machine_input.name
    message_body = {
        "changelog_number_start": state_machine_input.changelog_number_start,
        "changelog_number_end": state_machine_input.changelog_number_end,
        "type": state_machine_input.etl_type.value,
        "timestamp": state_machine_input.timestamp,
        "name": state_machine_name,
    }
    message_body_json = json.dumps(message_body)

    message_deduplication_id = str(uuid.uuid4())

    # Send the message to the SQS queue
    sqs_client.send_message(
        QueueUrl=cache["sqs_queue_url"],
        MessageBody=message_body_json,
        MessageGroupId="state_machine_group",
        MessageDeduplicationId=message_deduplication_id,
    )


steps = [
    _validate_no_changelog_number,
    _validate_database_is_empty,
    _create_state_machine_input,
    _copy_to_intermediate_history_file,
    _delete_trigger_object,
    _publish_message_to_sqs_queue,
]
