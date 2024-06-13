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
from etl_utils.trigger.model import StateMachineInputType, _create_timestamp
from etl_utils.trigger.operations import StateFileNotEmpty
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from mypy_boto3_stepfunctions import SFNClient

from etl.sds.executor.input.steps import _start_execution
from test_helpers.terraform import read_terraform_output

MOCKED_INPUT_TRIGGER_ENVIRONMENT = {
    "AWS_DEFAULT_REGION": "us-east-1",
    "STATE_MACHINE_ARN": "state-machine",
    "NOTIFY_LAMBDA_ARN": "notify-lambda",
    "TRUSTSTORE_BUCKET": "truststore",
    "CPM_FQDN": "cpm-fqdn",
    "LDAP_HOST": "ldap-host",
    "ETL_BUCKET": "etl-bucket",
    "LDAP_CHANGELOG_USER": "user",
    "LDAP_CHANGELOG_PASSWORD": "eggs",  # pragma: allowlist secret,
    "SQS_QUEUE_URL": "sqs-queue",
}

CHANGELOG_NUMBER_START = 546512
CHANGELOG_NUMBER_END = 548916
STATE_MACHINE_INPUT_TYPE_UPDATE = StateMachineInputType.UPDATE
STATE_MACHINE_INPUT_TYPE_BULK = StateMachineInputType.BULK
UPDATE_HISTORY_FILE = f"history/{STATE_MACHINE_INPUT_TYPE_UPDATE}.{CHANGELOG_NUMBER_START}.{CHANGELOG_NUMBER_END}.foo"
BULK_HISTORY_FILE = f"history/{STATE_MACHINE_INPUT_TYPE_BULK}.{CHANGELOG_NUMBER_START}.{CHANGELOG_NUMBER_END}.foo"
ETL_BUCKET = MOCKED_INPUT_TRIGGER_ENVIRONMENT["ETL_BUCKET"]


VALID_SQS_UPDATE_MESSAGE_BODY = json.dumps(
    {
        "changelog_number_start": CHANGELOG_NUMBER_START,
        "changelog_number_end": CHANGELOG_NUMBER_END,
        "etl_type": STATE_MACHINE_INPUT_TYPE_UPDATE,
        "timestamp": "foo",
        "name": f"{STATE_MACHINE_INPUT_TYPE_UPDATE}.{CHANGELOG_NUMBER_START}.{CHANGELOG_NUMBER_END}.foo",
    }
)
VALID_SQS_UPDATE_EVENT = {
    "Records": [
        {
            "messageId": "9eec100f-ee88-487a-80a7-3df7e40b780a",
            "receiptHandle": "xxx",
            "body": VALID_SQS_UPDATE_MESSAGE_BODY,
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-66605ea1-2906755913c79d1e09ac123c;Parent=2ead4ea5436a13b6;Sampled=0;Lineage=81989ed2:0",
                "SentTimestamp": "1717591754739",
                "SequenceNumber": "18886447562922735616",
                "MessageGroupId": "state_machine_group",
                "SenderId": "test",
                "MessageDeduplicationId": "155cca91-bd65-41a4-a335-922cde2edff9",
                "ApproximateFirstReceiveTimestamp": "1717591754739",
            },
            "messageAttributes": {},
            "md5OfBody": "xxx",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:*:nhse-cpm--megtest--sds--input-sqs.fifo",
            "awsRegion": "eu-west-2",
        }
    ]
}

VALID_SQS_BULK_MESSAGE_BODY = json.dumps(
    {
        "changelog_number_start": 0,
        "changelog_number_end": CHANGELOG_NUMBER_END,
        "etl_type": STATE_MACHINE_INPUT_TYPE_BULK,
        "timestamp": "foo",
        "name": f"{STATE_MACHINE_INPUT_TYPE_BULK}.{CHANGELOG_NUMBER_START}.{CHANGELOG_NUMBER_END}.foo",
    }
)
VALID_SQS_BULK_EVENT = {
    "Records": [
        {
            "messageId": "9eec100f-ee88-487a-80a7-3df7e40b780a",
            "receiptHandle": "xxx",
            "body": VALID_SQS_BULK_MESSAGE_BODY,
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-66605ea1-2906755913c79d1e09ac123c;Parent=2ead4ea5436a13b6;Sampled=0;Lineage=81989ed2:0",
                "SentTimestamp": "1717591754739",
                "SequenceNumber": "18886447562922735616",
                "MessageGroupId": "state_machine_group",
                "SenderId": "test",
                "MessageDeduplicationId": "155cca91-bd65-41a4-a335-922cde2edff9",
                "ApproximateFirstReceiveTimestamp": "1717591754739",
            },
            "messageAttributes": {},
            "md5OfBody": "xxx",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:*:nhse-cpm--megtest--sds--input-sqs.fifo",
            "awsRegion": "eu-west-2",
        }
    ]
}

INVALID_BODY_FIELD_SQS_MESSAGE = json.dumps({"invalid field": "value"})
INVALID_BODY_FIELD_EVENT = {
    "Records": [
        {
            "messageId": "9eec100f-ee88-487a-80a7-3df7e40b780a",
            "receiptHandle": "xxx",
            "body": INVALID_BODY_FIELD_SQS_MESSAGE,
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-66605ea1-2906755913c79d1e09ac123c;Parent=2ead4ea5436a13b6;Sampled=0;Lineage=81989ed2:0",
                "SentTimestamp": "1717591754739",
                "SequenceNumber": "18886447562922735616",
                "MessageGroupId": "state_machine_group",
                "SenderId": "test",
                "MessageDeduplicationId": "155cca91-bd65-41a4-a335-922cde2edff9",
                "ApproximateFirstReceiveTimestamp": "1717591754739",
            },
            "messageAttributes": {},
            "md5OfBody": "xxx",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:*:nhse-cpm--megtest--sds--input-sqs.fifo",
            "awsRegion": "eu-west-2",
        }
    ]
}

INVALID_BODY_JSON_SQS_MESSAGE = '{invalid_json: "value"}'
INVALID_BODY_JSON_EVENT = {
    "Records": [
        {
            "messageId": "9eec100f-ee88-487a-80a7-3df7e40b780a",
            "receiptHandle": "xxx",
            "body": INVALID_BODY_JSON_SQS_MESSAGE,
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-66605ea1-2906755913c79d1e09ac123c;Parent=2ead4ea5436a13b6;Sampled=0;Lineage=81989ed2:0",
                "SentTimestamp": "1717591754739",
                "SequenceNumber": "18886447562922735616",
                "MessageGroupId": "state_machine_group",
                "SenderId": "test",
                "MessageDeduplicationId": "155cca91-bd65-41a4-a335-922cde2edff9",
                "ApproximateFirstReceiveTimestamp": "1717591754739",
            },
            "messageAttributes": {},
            "md5OfBody": "xxx",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:*:nhse-cpm--megtest--sds--input-sqs.fifo",
            "awsRegion": "eu-west-2",
        }
    ]
}


@pytest.mark.parametrize(
    ("message", "history_file"),
    [
        (VALID_SQS_UPDATE_EVENT, UPDATE_HISTORY_FILE),
        (VALID_SQS_BULK_EVENT, BULK_HISTORY_FILE),
    ],
    indirect=False,
)
def test_input_state_lock_does_not_exist(message, history_file):
    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_INPUT_TRIGGER_ENVIRONMENT, clear=True
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

        from etl.sds.executor.input import input

        # Mock the cache contents
        input.CACHE["s3_client"] = s3_client

        # Remove start execution, since it's meaningless
        if _start_execution in input.steps:
            idx = input.steps.index(_start_execution)
            input.steps.pop(idx)

        # Don't execute the notify lambda
        input.notify = lambda lambda_client, function_name, result, trigger_type: result

        # Execute input lambda
        response = input.handler(event=message)

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
    ("message", "history_file"),
    [
        (VALID_SQS_UPDATE_EVENT, UPDATE_HISTORY_FILE),
        (VALID_SQS_BULK_EVENT, BULK_HISTORY_FILE),
    ],
    indirect=False,
)
def test_input_state_lock_exist(message, history_file):
    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_INPUT_TRIGGER_ENVIRONMENT, clear=True
    ), mock.patch("etl_utils.trigger.model.datetime") as mocked_datetime:
        mocked_datetime.datetime.now().isoformat.return_value = "foo"
        s3_client = boto3.client("s3")

        # Create history file & state lock
        s3_client.create_bucket(Bucket=ETL_BUCKET)
        s3_client.put_object(
            Bucket=ETL_BUCKET,
            Key=f"{history_file}",
            Body="test-changes",
        )

        s3_client.put_object(
            Bucket=ETL_BUCKET,
            Key=ETL_STATE_LOCK,
            Body="test-lock",
        )

        from etl.sds.executor.input import input

        # Mock the cache contents
        input.CACHE["s3_client"] = s3_client

        # Don't execute the notify lambda
        input.notify = lambda lambda_client, function_name, result, trigger_type: result

        # Execute input lambda
        input.handler(event=message)

        # Assert history file deleted
        with pytest.raises(ClientError):
            s3_client.get_object(Bucket=ETL_BUCKET, Key=f"{history_file}")

        # Assert state lock still active
        s3_client.get_object(Bucket=ETL_BUCKET, Key=ETL_STATE_LOCK)


# test process message
@pytest.mark.parametrize(
    "message",
    [VALID_SQS_UPDATE_EVENT, VALID_SQS_BULK_EVENT],
)
def test_input_failure_state_file_not_empty(message):
    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_INPUT_TRIGGER_ENVIRONMENT, clear=True
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

        from etl.sds.executor.input import input

        # Mock the cache contents
        input.CACHE["s3_client"] = s3_client

        # Don't execute the notify lambda
        input.notify = lambda lambda_client, function_name, result, trigger_type: result

        # Execute input lambda
        result = input.process_message(message=message["Records"][0])

        assert isinstance(result, StateFileNotEmpty)


@pytest.mark.parametrize(
    "message",
    [INVALID_BODY_JSON_EVENT],
)
def test_input_failure_invalid_json_message(message):
    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_INPUT_TRIGGER_ENVIRONMENT, clear=True
    ), mock.patch("etl_utils.trigger.model.datetime") as mocked_datetime:
        mocked_datetime.datetime.now().isoformat.return_value = "foo"
        s3_client = boto3.client("s3")

        from etl.sds.executor.input import input

        # Mock the cache contents
        input.CACHE["s3_client"] = s3_client

        # Remove start execution, since it's meaningless
        if _start_execution in input.steps:
            idx = input.steps.index(_start_execution)
            input.steps.pop(idx)

        # Don't execute the notify lambda
        input.notify = lambda lambda_client, function_name, result, trigger_type: result

        # Execute input lambda
        result = input.process_message(message=message["Records"][0])

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
def test_input_trigger_update_success():
    # Where the state is located
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    sqs_queue_url = read_terraform_output("sds_etl.value.proxy_executer.sqs_queue_url")
    state_machine_arn = read_terraform_output("sds_etl.value.state_machine_arn")
    timestamp = _create_timestamp().replace(":", ".")
    intermediate_history_file = f"history/{STATE_MACHINE_INPUT_TYPE_UPDATE}.{UPDATE_CHANGELOG_NUMBER_START}.{UPDATE_CHANGELOG_NUMBER_END}.{timestamp}"
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
    s3_client.put_object(Bucket=etl_bucket, Key=intermediate_history_file, Body=b"")
    s3_client.delete_object(Bucket=etl_bucket, Key=ETL_STATE_LOCK)

    # Trigger the input lambda by sending message to queue
    sqs_client = boto3.client("sqs")
    response = sqs_client.send_message(
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
    state_machine_successful = False
    etl_state_lock_removed = False
    while not all(
        (
            changelog_number_updated,
            state_machine_successful,
            etl_state_lock_removed,
        )
    ):
        time.sleep(5)
        changelog_number_updated = (
            changelog_number_updated or was_changelog_number_updated()
        )
        state_machine_successful = (
            state_machine_successful or was_state_machine_successful()
        )
        etl_state_lock_removed = etl_state_lock_removed or was_etl_state_lock_removed()

    # Confirm the final state
    assert changelog_number_updated
    assert state_machine_successful
    assert etl_state_lock_removed


@pytest.mark.timeout(30)
@pytest.mark.integration
def test_input_trigger_update_rejected():
    # Where the state is located
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    sqs_queue_url = read_terraform_output("sds_etl.value.proxy_executer.sqs_queue_url")
    timestamp = _create_timestamp().replace(":", ".")
    intermediate_history_file = f"history/{STATE_MACHINE_INPUT_TYPE_UPDATE}.{UPDATE_CHANGELOG_NUMBER_START}.{UPDATE_CHANGELOG_NUMBER_END}.{timestamp}"

    # Set some questions
    s3_client = boto3.client("s3")
    ask_s3 = partial(_ask_s3, s3_client=s3_client, bucket=etl_bucket)

    was_changelog_number_not_updated = lambda: ask_s3(
        key=CHANGELOG_NUMBER,
        question=lambda x: str(UPDATE_CHANGELOG_NUMBER_START).encode("utf-8"),
    )
    was_etl_state_lock_not_removed = lambda: ask_s3(key=ETL_STATE_LOCK)
    was_intermediate_history_file_deleted = lambda: not ask_s3(
        key=intermediate_history_file
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
    s3_client.put_object(Bucket=etl_bucket, Key=intermediate_history_file, Body=b"")
    s3_client.put_object(Bucket=etl_bucket, Key=ETL_STATE_LOCK, Body="locked")

    # Trigger the input lambda by sending message to queue
    sqs_client = boto3.client("sqs")
    response = sqs_client.send_message(
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
    intermediate_history_file_deleted = False
    while not all(
        (
            changelog_number_not_updated,
            etl_state_lock_not_removed,
            intermediate_history_file_deleted,
        )
    ):
        time.sleep(5)
        changelog_number_not_updated = (
            changelog_number_not_updated or was_changelog_number_not_updated()
        )
        etl_state_lock_not_removed = (
            etl_state_lock_not_removed or was_etl_state_lock_not_removed()
        )
        intermediate_history_file_deleted = (
            intermediate_history_file_deleted or was_intermediate_history_file_deleted()
        )

    # Confirm the final state
    assert changelog_number_not_updated
    assert etl_state_lock_not_removed
    assert intermediate_history_file_deleted
