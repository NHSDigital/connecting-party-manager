import time
from collections import deque
from functools import partial
from json import JSONDecodeError
from types import FunctionType

import boto3
import pytest
from botocore.exceptions import ClientError
from domain.core.device import DeviceType
from etl_utils.constants import CHANGELOG_NUMBER, ETL_STATE_LOCK, WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from event.aws.client import dynamodb_client
from event.json import json_loads
from mypy_boto3_s3 import S3Client

from etl.sds.worker.extract.tests.test_extract_worker import GOOD_SDS_RECORD
from etl.sds.worker.load.tests.test_load_worker import MockDeviceRepository
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output

TEST_DATA_NAME = "123.ldif"
EXPECTED_CHANGELOG_NUMBER = 123
EMPTY_LDIF_DATA = b""
EMPTY_JSON_DATA = deque()
ALLOWED_EXCEPTIONS = (JSONDecodeError,)


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


def _ask_s3_prefix(
    s3_client: S3Client, bucket: str, key_prefix: str, question: FunctionType = None
):
    result = False

    response = s3_client.list_objects(Bucket=bucket, Prefix=key_prefix)

    for item in response.get("Contents", []):
        if item and question is not None:
            result = _ask_s3(
                s3_client=s3_client, bucket=bucket, key=item["Key"], question=question
            )
    return result


@pytest.mark.timeout(20)
@pytest.mark.integration
def test_bulk_trigger():
    # Where the state is located
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    bulk_trigger_prefix = read_terraform_output("sds_etl.value.bulk_trigger_prefix")
    initial_trigger_key = f"{bulk_trigger_prefix}/{TEST_DATA_NAME}"
    history_key_prefix = f"history/bulk"
    table_name = read_terraform_output("dynamodb_table_name.value")

    client = dynamodb_client()
    repository = MockDeviceRepository(table_name=table_name, dynamodb_client=client)

    # Set some questions
    s3_client = boto3.client("s3")
    ask_s3 = partial(_ask_s3, s3_client=s3_client, bucket=etl_bucket)
    ask_s3_prefix = partial(_ask_s3_prefix, s3_client=s3_client, bucket=etl_bucket)

    was_trigger_key_deleted = lambda: not ask_s3(key=initial_trigger_key)
    was_trigger_key_moved_to_history = lambda: ask_s3_prefix(
        key_prefix=history_key_prefix, question=lambda x: x == GOOD_SDS_RECORD.encode()
    )
    was_changelog_number_updated = lambda: ask_s3(
        key=CHANGELOG_NUMBER,
        question=lambda x: json_loads(x) == EXPECTED_CHANGELOG_NUMBER,
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
        and repository.count(by=DeviceType.PRODUCT) > 0
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
    s3_client.delete_object(Bucket=etl_bucket, Key=initial_trigger_key)

    history_files = s3_client.list_objects(Bucket=etl_bucket, Prefix=history_key_prefix)
    for item in history_files.get("Contents", []):
        s3_client.delete_object(Bucket=etl_bucket, Key=item["Key"])

    s3_client.delete_object(Bucket=etl_bucket, Key=CHANGELOG_NUMBER)
    s3_client.delete_object(Bucket=etl_bucket, Key=ETL_STATE_LOCK)
    clear_dynamodb_table(client=client, table_name=table_name)

    # Trigger the bulk load
    s3_client.put_object(
        Bucket=etl_bucket, Key=initial_trigger_key, Body=GOOD_SDS_RECORD.encode()
    )

    trigger_key_deleted = False
    trigger_key_moved_to_history = False
    changelog_number_updated = False
    state_machine_successful = False
    etl_state_lock_removed = False
    while not all(
        (
            trigger_key_deleted,
            trigger_key_moved_to_history,
            changelog_number_updated,
            state_machine_successful,
            etl_state_lock_removed,
        )
    ):
        time.sleep(5)
        trigger_key_deleted = trigger_key_deleted or was_trigger_key_deleted()
        trigger_key_moved_to_history = (
            trigger_key_moved_to_history or was_trigger_key_moved_to_history()
        )
        changelog_number_updated = (
            changelog_number_updated or was_changelog_number_updated()
        )
        state_machine_successful = (
            state_machine_successful or was_state_machine_successful()
        )
        etl_state_lock_removed = etl_state_lock_removed or was_etl_state_lock_removed()

    # Confirm the final state
    assert trigger_key_deleted
    assert trigger_key_moved_to_history
    assert changelog_number_updated
    assert state_machine_successful
    assert etl_state_lock_removed
