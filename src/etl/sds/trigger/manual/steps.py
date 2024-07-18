import uuid
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from etl_utils.constants import ETL_STATE_MACHINE_HISTORY
from etl_utils.trigger.model import StateMachineInput
from event.step_chain import StepChain

from .operations import validate_bucket_contents

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_sqs import SQSClient


class ExecutionRunningError(Exception):
    """Custom exception for existing ETL execution Running."""

    pass


class StateMachineError(Exception):
    """Custom exception for problem getting executions."""

    pass


class Cache(TypedDict):
    s3_client: "S3Client"
    sqs_client: "SQSClient"
    sf_client: "SFClient"
    state_machine_arn: str
    etl_bucket: str


def _check_execution_running(data, cache):
    _, _, state_machine_arn = data[StepChain.INIT]
    sf_client = cache["sf_client"]
    try:
        executions = sf_client.list_executions(
            stateMachineArn=state_machine_arn, maxResults=1, statusFilter="RUNNING"
        )
        if executions["executions"]:
            raise ExecutionRunningError("An execution is Running.")
    except:
        return True


def _find_last_execution(data, cache):
    etl_bucket, _, _ = data[StepChain.INIT]
    response = validate_bucket_contents(
        s3_client=cache["s3_client"], etl_bucket=etl_bucket
    )
    latest_execution = max(response["Contents"], key=lambda obj: obj["LastModified"])
    return latest_execution["Key"]


def _set_etl_type(data, cache):
    execution = data[_find_last_execution]
    object_name = execution.replace(f"{ETL_STATE_MACHINE_HISTORY}/", "", 1)
    etl_type = object_name.split(".")
    return etl_type[0], etl_type[1], etl_type[2]


def _create_state_machine_input(data, cache):
    etl_exc, current_changelog_number, latest_changelog_number = data[_set_etl_type]
    if etl_exc.upper() != "BULK":
        return StateMachineInput.update(
            changelog_number_start=current_changelog_number,
            changelog_number_end=latest_changelog_number,
            manual_retry=True,
        )
    return StateMachineInput.bulk(
        changelog_number=Path(latest_changelog_number).stem, manual_retry=True
    )


def _publish_message_to_sqs_queue(data, cache: Cache):
    state_machine_input: StateMachineInput = data[_create_state_machine_input]
    etl_exc, _, _ = data[_set_etl_type]
    message_body = state_machine_input.json_with_name()
    message_deduplication_id = str(uuid.uuid4())

    # Send the message to the SQS queue
    cache["sqs_client"].send_message(
        QueueUrl=cache["sqs_queue_url"],
        MessageBody=message_body,
        MessageGroupId="state_machine_group",
        MessageDeduplicationId=message_deduplication_id,
    )

    return etl_exc


steps = [
    _check_execution_running,
    _find_last_execution,
    _set_etl_type,
    _create_state_machine_input,
    _publish_message_to_sqs_queue,
]
