import json
import os
import time
import uuid
from collections import deque
from functools import partial
from types import FunctionType
from unittest import mock

import boto3
import pytest
from botocore.exceptions import ClientError
from etl_utils.constants import CHANGELOG_NUMBER, ETL_STATE_LOCK, WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from etl_utils.trigger.model import _create_timestamp
from etl_utils.trigger.operations import StateFileNotEmpty
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from mypy_boto3_stepfunctions import SFNClient

from etl.sds.etl_state_lock_enforcer.steps import _start_execution
from test_helpers.sample_sqs_messages import (
    INVALID_BODY_JSON_EVENT,
    QUEUE_BULK_HISTORY_FILE,
    QUEUE_UPDATE_HISTORY_FILE,
    STATE_MACHINE_BULK_HISTORY_FILE,
    STATE_MACHINE_INPUT_TYPE_UPDATE,
    STATE_MACHINE_UPDATE_HISTORY_FILE,
    VALID_SQS_BULK_EVENT,
    VALID_SQS_UPDATE_EVENT,
)
from test_helpers.terraform import read_terraform_output

MOCKED_ETL_STATE_LOCK_ENFORCER_ENVIRONMENT = {
    "AWS_DEFAULT_REGION": "us-east-1",
    "STATE_MACHINE_ARN": "state-machine",
    "NOTIFY_LAMBDA_ARN": "notify-lambda",
    "ETL_BUCKET": "etl-bucket",
    "SQS_QUEUE_URL": "sqs-queue",
}

ETL_BUCKET = MOCKED_ETL_STATE_LOCK_ENFORCER_ENVIRONMENT["ETL_BUCKET"]


@pytest.mark.parametrize(
    ("message", "history_file"),
    [
        (VALID_SQS_UPDATE_EVENT, QUEUE_UPDATE_HISTORY_FILE),
        (VALID_SQS_BULK_EVENT, QUEUE_BULK_HISTORY_FILE),
    ],
    indirect=False,
)
def test_etl_state_lock_enforcer_state_lock_does_not_exist(message, history_file):
    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_ETL_STATE_LOCK_ENFORCER_ENVIRONMENT, clear=True
    ), mock.patch("etl_utils.trigger.model.datetime") as mocked_datetime:
        mocked_datetime.datetime.now().isoformat.return_value = "foo"
        s3_client = boto3.client("s3")

        # Create history file
        s3_client.create_bucket(Bucket=ETL_BUCKET)
        s3_client.put_object(
            Bucket=ETL_BUCKET,
            Key=f"{history_file}",
            Body="test",
        )

        from etl.sds.etl_state_lock_enforcer import etl_state_lock_enforcer

        # Mock the cache contents
        etl_state_lock_enforcer.CACHE["s3_client"] = s3_client

        # Remove start execution, since it's meaningless for unit tests
        if _start_execution in etl_state_lock_enforcer.steps:
            idx = etl_state_lock_enforcer.steps.index(_start_execution)
            etl_state_lock_enforcer.steps.pop(idx)

        # Don't execute the notify lambda
        etl_state_lock_enforcer.notify = (
            lambda lambda_client, function_name, result, trigger_type: result
        )

        # Execute etl_state_lock_enforcer lambda
        response = etl_state_lock_enforcer.handler(event=message)

        # Assert state_lock_file created
        etl_state_lock_file = s3_client.get_object(
            Bucket=ETL_BUCKET, Key=ETL_STATE_LOCK
        )
        assert etl_state_lock_file

        # Assert changes put to state machine
        state_machine_input = s3_client.get_object(
            Bucket=ETL_BUCKET,
            Key="input--extract/unprocessed",
        )
        assert state_machine_input


@pytest.mark.parametrize(
    ("message", "queue_history_file", "state_machine_history_file"),
    [
        (
            VALID_SQS_UPDATE_EVENT,
            QUEUE_UPDATE_HISTORY_FILE,
            STATE_MACHINE_UPDATE_HISTORY_FILE,
        ),
        (
            VALID_SQS_BULK_EVENT,
            QUEUE_BULK_HISTORY_FILE,
            STATE_MACHINE_BULK_HISTORY_FILE,
        ),
    ],
    indirect=False,
)
def test_etl_state_lock_enforcer_state_lock_exist(
    message, queue_history_file, state_machine_history_file
):
    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_ETL_STATE_LOCK_ENFORCER_ENVIRONMENT, clear=True
    ), mock.patch("etl_utils.trigger.model.datetime") as mocked_datetime:
        mocked_datetime.datetime.now().isoformat.return_value = "foo"
        s3_client = boto3.client("s3")

        # Create intermediate history file & state lock
        s3_client.create_bucket(Bucket=ETL_BUCKET)
        s3_client.put_object(
            Bucket=ETL_BUCKET,
            Key=f"{queue_history_file}",
            Body="test-changes",
        )

        s3_client.put_object(
            Bucket=ETL_BUCKET,
            Key=ETL_STATE_LOCK,
            Body="test-lock",
        )

        from etl.sds.etl_state_lock_enforcer import etl_state_lock_enforcer

        # Mock the cache contents
        etl_state_lock_enforcer.CACHE["s3_client"] = s3_client

        # Don't execute the notify lambda
        etl_state_lock_enforcer.notify = (
            lambda lambda_client, function_name, result, trigger_type: result
        )

        # Execute etl_state_lock_enforcer lambda
        etl_state_lock_enforcer.handler(event=message)

        # Assert history file deleted
        with pytest.raises(ClientError):
            s3_client.get_object(Bucket=ETL_BUCKET, Key=f"{state_machine_history_file}")

        # Assert state lock still active
        s3_client.get_object(Bucket=ETL_BUCKET, Key=ETL_STATE_LOCK)


# test process message
@pytest.mark.parametrize(
    "message",
    [VALID_SQS_UPDATE_EVENT, VALID_SQS_BULK_EVENT],
)
def test_etl_state_lock_enforcer_failure_state_file_not_empty(message):
    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_ETL_STATE_LOCK_ENFORCER_ENVIRONMENT, clear=True
    ), mock.patch("etl_utils.trigger.model.datetime") as mocked_datetime:
        mocked_datetime.datetime.now().isoformat.return_value = "foo"
        s3_client = boto3.client("s3")

        # Create state file contents
        s3_client.create_bucket(Bucket=ETL_BUCKET)
        s3_client.put_object(
            Bucket=ETL_BUCKET,
            Key="input--extract/unprocessed",
            Body="test",
        )
        s3_client.put_object(
            Bucket=ETL_BUCKET,
            Key="input--transform/unprocessed",
            Body="test",
        )
        s3_client.put_object(
            Bucket=ETL_BUCKET,
            Key="input--load/unprocessed",
            Body="test",
        )

        from etl.sds.etl_state_lock_enforcer import etl_state_lock_enforcer

        # Mock the cache contents
        etl_state_lock_enforcer.CACHE["s3_client"] = s3_client

        # Don't execute the notify lambda
        etl_state_lock_enforcer.notify = (
            lambda lambda_client, function_name, result, trigger_type: result
        )

        # Execute etl_state_lock_enforcer lambda
        result = etl_state_lock_enforcer.process_message(message=message["Records"][0])

        assert isinstance(result, StateFileNotEmpty)


@pytest.mark.parametrize(
    "message",
    [INVALID_BODY_JSON_EVENT],
)
def test_etl_state_lock_enforcer_failure_invalid_json_message(message):
    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_ETL_STATE_LOCK_ENFORCER_ENVIRONMENT, clear=True
    ), mock.patch("etl_utils.trigger.model.datetime") as mocked_datetime:
        mocked_datetime.datetime.now().isoformat.return_value = "foo"
        s3_client = boto3.client("s3")

        from etl.sds.etl_state_lock_enforcer import etl_state_lock_enforcer

        # Mock the cache contents
        etl_state_lock_enforcer.CACHE["s3_client"] = s3_client

        # Don't execute the notify lambda
        etl_state_lock_enforcer.notify = (
            lambda lambda_client, function_name, result, trigger_type: result
        )

        # Execute etl_state_lock_enforcer lambda
        result = etl_state_lock_enforcer.process_message(message=message["Records"][0])

        assert isinstance(result, json.decoder.JSONDecodeError)


# Integration test
UPDATE_CHANGELOG_NUMBER_START = 123
UPDATE_CHANGELOG_NUMBER_END = 124
EMPTY_LDIF_DATA = b""
EMPTY_JSON_DATA = deque()
ALLOWED_EXCEPTIONS = (json.JSONDecodeError,)


def _ask_s3(s3_client: S3Client, bucket: str, key: str, question: FunctionType = None):
    result = True
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
    except ClientError:
        result = False

    if result and question is not None:
        data = response["Body"].read()
        try:
            result = question(data)
        except ALLOWED_EXCEPTIONS:
            result = False
    return result


def _ask_step_functions(
    step_functions_client: SFNClient,
    execution_arn: str,
    question: FunctionType = None,
):
    status = ""
    try:
        execution_state = step_functions_client.describe_execution(
            executionArn=execution_arn,
        )
        status = execution_state["status"]
    except ClientError:
        status = "FAILED"

    if status and question is not None:
        status = question(status)
    return status


@pytest.mark.timeout(30)
@pytest.mark.integration
def test_etl_state_lock_enforcer_trigger_update_success():
    # Where the state is located
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    sqs_queue_url = read_terraform_output(
        "sds_etl.value.etl_state_lock_enforcer.sqs_queue_url"
    )
    state_machine_arn = read_terraform_output("sds_etl.value.state_machine_arn")
    timestamp = _create_timestamp().replace(":", ".")
    intermediate_queue_history_file = f"etl_queue_history/{STATE_MACHINE_INPUT_TYPE_UPDATE}.{UPDATE_CHANGELOG_NUMBER_START}.{UPDATE_CHANGELOG_NUMBER_END}.{timestamp}"
    state_machine_history_file = f"etl_state_machine_history/{STATE_MACHINE_INPUT_TYPE_UPDATE}.{UPDATE_CHANGELOG_NUMBER_START}.{UPDATE_CHANGELOG_NUMBER_END}.{timestamp}"
    execution_arn = f"{state_machine_arn}:{STATE_MACHINE_INPUT_TYPE_UPDATE}.{UPDATE_CHANGELOG_NUMBER_START}.{UPDATE_CHANGELOG_NUMBER_END}.{timestamp}".replace(
        "stateMachine", "execution"
    )

    # Set some questions
    s3_client = boto3.client("s3")
    ask_s3 = partial(_ask_s3, s3_client=s3_client, bucket=etl_bucket)
    step_functions_client = boto3.client("stepfunctions")
    ask_step_functions = partial(
        _ask_step_functions,
        step_functions_client=step_functions_client,
    )

    was_changelog_number_updated = lambda: ask_s3(
        key=CHANGELOG_NUMBER,
        question=lambda x: str(UPDATE_CHANGELOG_NUMBER_END).encode("utf-8"),
    )
    was_state_machine_history_file_created = lambda: ask_s3(
        key=state_machine_history_file
    )
    was_state_machine_successful = (
        lambda: ask_s3(
            key=WorkerKey.EXTRACT,
            question=lambda x: x == b"",
        )
        and ask_s3(
            key=WorkerKey.TRANSFORM,
            question=lambda x: pkl_loads_lz4(x) == deque(),
        )
        and ask_s3(
            key=WorkerKey.LOAD,
            question=lambda x: pkl_loads_lz4(x) == deque(),
        )
        and ask_step_functions(
            execution_arn=execution_arn, question=lambda x: x == "SUCCEEDED"
        )
    )
    was_etl_state_lock_removed = lambda: not ask_s3(key=ETL_STATE_LOCK)

    # Clear/set the initial state
    s3_client.put_object(Bucket=etl_bucket, Key=WorkerKey.EXTRACT, Body=EMPTY_LDIF_DATA)
    s3_client.put_object(
        Bucket=etl_bucket, Key=WorkerKey.TRANSFORM, Body=pkl_dumps_lz4(EMPTY_JSON_DATA)
    )
    s3_client.put_object(
        Bucket=etl_bucket, Key=WorkerKey.LOAD, Body=pkl_dumps_lz4(EMPTY_JSON_DATA)
    )
    s3_client.put_object(
        Bucket=etl_bucket,
        Key=CHANGELOG_NUMBER,
        Body=str(UPDATE_CHANGELOG_NUMBER_START).encode("utf-8"),
    )
    s3_client.put_object(
        Bucket=etl_bucket, Key=intermediate_queue_history_file, Body=b""
    )
    s3_client.delete_object(Bucket=etl_bucket, Key=ETL_STATE_LOCK)

    # Trigger the etl_state_lock_enforcer lambda by sending message to queue
    sqs_client = boto3.client("sqs")
    sqs_client.send_message(
        QueueUrl=f"{sqs_queue_url}",
        MessageBody=json.dumps(
            {
                "changelog_number_start": UPDATE_CHANGELOG_NUMBER_START,
                "changelog_number_end": UPDATE_CHANGELOG_NUMBER_END,
                "etl_type": STATE_MACHINE_INPUT_TYPE_UPDATE,
                "timestamp": f"{timestamp}",
                "name": f"{STATE_MACHINE_INPUT_TYPE_UPDATE}.{UPDATE_CHANGELOG_NUMBER_START}.{UPDATE_CHANGELOG_NUMBER_END}.{timestamp}",
            }
        ),
        MessageDeduplicationId=str(uuid.uuid4()),
        MessageGroupId="state_machine_group",
    )

    changelog_number_updated = False
    state_machine_history_file_created = False
    state_machine_successful = False
    etl_state_lock_removed = False
    while not all(
        (
            changelog_number_updated,
            state_machine_history_file_created,
            state_machine_successful,
            etl_state_lock_removed,
        )
    ):
        time.sleep(5)
        changelog_number_updated = (
            changelog_number_updated or was_changelog_number_updated()
        )
        state_machine_history_file_created = (
            state_machine_history_file_created
            or was_state_machine_history_file_created()
        )
        state_machine_successful = (
            state_machine_successful or was_state_machine_successful()
        )
        etl_state_lock_removed = etl_state_lock_removed or was_etl_state_lock_removed()

    # Confirm the final state
    assert changelog_number_updated
    assert state_machine_history_file_created
    assert state_machine_successful
    assert etl_state_lock_removed


@pytest.mark.timeout(30)
@pytest.mark.integration
def test_etl_state_lock_enforcer_trigger_update_rejected():
    # Where the state is located
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    sqs_queue_url = read_terraform_output(
        "sds_etl.value.etl_state_lock_enforcer.sqs_queue_url"
    )
    timestamp = _create_timestamp().replace(":", ".")
    intermediate_queue_history_file = f"etl_queue_history/{STATE_MACHINE_INPUT_TYPE_UPDATE}.{UPDATE_CHANGELOG_NUMBER_START}.{UPDATE_CHANGELOG_NUMBER_END}.{timestamp}"
    state_machine_history_file = f"etl_state_machine_history/{STATE_MACHINE_INPUT_TYPE_UPDATE}.{UPDATE_CHANGELOG_NUMBER_START}.{UPDATE_CHANGELOG_NUMBER_END}.{timestamp}"

    # Set some questions
    s3_client = boto3.client("s3")
    ask_s3 = partial(_ask_s3, s3_client=s3_client, bucket=etl_bucket)

    was_changelog_number_not_updated = lambda: ask_s3(
        key=CHANGELOG_NUMBER,
        question=lambda x: str(UPDATE_CHANGELOG_NUMBER_START).encode("utf-8"),
    )
    was_etl_state_lock_not_removed = lambda: ask_s3(key=ETL_STATE_LOCK)
    was_state_machine_history_file_not_created = lambda: not ask_s3(
        key=state_machine_history_file
    )

    # Clear/set the initial state
    s3_client.put_object(Bucket=etl_bucket, Key=WorkerKey.EXTRACT, Body=EMPTY_LDIF_DATA)
    s3_client.put_object(
        Bucket=etl_bucket, Key=WorkerKey.TRANSFORM, Body=pkl_dumps_lz4(EMPTY_JSON_DATA)
    )
    s3_client.put_object(
        Bucket=etl_bucket, Key=WorkerKey.LOAD, Body=pkl_dumps_lz4(EMPTY_JSON_DATA)
    )
    s3_client.put_object(
        Bucket=etl_bucket,
        Key=CHANGELOG_NUMBER,
        Body=str(UPDATE_CHANGELOG_NUMBER_START).encode("utf-8"),
    )
    s3_client.put_object(
        Bucket=etl_bucket, Key=intermediate_queue_history_file, Body=b""
    )
    s3_client.put_object(Bucket=etl_bucket, Key=ETL_STATE_LOCK, Body="locked")

    # Trigger the etl_state_lock_enforcer lambda by sending message to queue
    sqs_client = boto3.client("sqs")
    sqs_client.send_message(
        QueueUrl=f"{sqs_queue_url}",
        MessageBody=json.dumps(
            {
                "changelog_number_start": UPDATE_CHANGELOG_NUMBER_START,
                "changelog_number_end": UPDATE_CHANGELOG_NUMBER_END,
                "etl_type": STATE_MACHINE_INPUT_TYPE_UPDATE,
                "timestamp": f"{timestamp}",
                "name": f"{STATE_MACHINE_INPUT_TYPE_UPDATE}.{UPDATE_CHANGELOG_NUMBER_START}.{UPDATE_CHANGELOG_NUMBER_END}.{timestamp}",
            }
        ),
        MessageDeduplicationId=str(uuid.uuid4()),
        MessageGroupId="state_machine_group",
    )

    changelog_number_not_updated = False
    etl_state_lock_not_removed = False
    state_machine_history_file_not_created = False
    while not all(
        (
            changelog_number_not_updated,
            etl_state_lock_not_removed,
            state_machine_history_file_not_created,
        )
    ):
        time.sleep(5)
        changelog_number_not_updated = (
            changelog_number_not_updated or was_changelog_number_not_updated()
        )
        etl_state_lock_not_removed = (
            etl_state_lock_not_removed or was_etl_state_lock_not_removed()
        )
        state_machine_history_file_not_created = (
            state_machine_history_file_not_created
            or was_state_machine_history_file_not_created()
        )

    # Confirm the final state
    assert changelog_number_not_updated
    assert etl_state_lock_not_removed
    assert state_machine_history_file_not_created
