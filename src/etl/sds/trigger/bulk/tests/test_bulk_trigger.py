import json
import time
from functools import partial
from json import JSONDecodeError
from types import FunctionType

import boto3
import pytest
from botocore.exceptions import ClientError
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from event.json import json_loads
from mypy_boto3_s3 import S3Client

from etl.sds.tests.test_sds_etl_components import GOOD_SDS_RECORD_AS_JSON
from etl.sds.worker.extract.tests.test_extract_worker import GOOD_SDS_RECORD
from test_helpers.terraform import read_terraform_output

TEST_DATA_NAME = "test.ldif"
EXPECTED_CHANGELOG_NUMBER = "0"
EMPTY_LDIF_DATA = b""
EMPTY_JSON_DATA = json.dumps([]).encode()
ALLOWED_EXCEPTIONS = (JSONDecodeError,)


def _ask_s3(s3_client: S3Client, bucket: str, key: str, question: FunctionType = None):
    result = True
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
    except ClientError:
        result = False

    if result and question is not None:
        data = response["Body"].read().decode()
        try:
            result = question(data)
        except ALLOWED_EXCEPTIONS:
            result = False
    return result


@pytest.mark.timeout(30)
@pytest.mark.integration
def test_bulk_trigger():
    # Where the state is located
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    bulk_trigger_prefix = read_terraform_output("sds_etl.value.bulk_trigger_prefix")
    initial_trigger_key = f"{bulk_trigger_prefix}/{TEST_DATA_NAME}"
    final_trigger_key = f"history/{bulk_trigger_prefix}/{TEST_DATA_NAME}"

    # Set some questions
    s3_client = boto3.client("s3")
    ask_s3 = partial(_ask_s3, s3_client=s3_client, bucket=etl_bucket)

    was_trigger_key_deleted = lambda: not ask_s3(key=initial_trigger_key)
    was_trigger_key_moved_to_history = lambda: ask_s3(
        key=final_trigger_key, question=lambda x: x == GOOD_SDS_RECORD
    )
    was_changelog_number_updated = lambda: ask_s3(
        key=CHANGELOG_NUMBER,
        question=lambda x: json_loads(x) == EXPECTED_CHANGELOG_NUMBER,
    )
    was_state_machine_successful = lambda: ask_s3(
        key=WorkerKey.TRANSFORM,
        question=lambda x: json_loads(x) == [GOOD_SDS_RECORD_AS_JSON],
    )

    # Clear/set the initial state
    s3_client.put_object(Bucket=etl_bucket, Key=WorkerKey.EXTRACT, Body=EMPTY_LDIF_DATA)
    s3_client.put_object(
        Bucket=etl_bucket, Key=WorkerKey.TRANSFORM, Body=EMPTY_JSON_DATA
    )
    s3_client.put_object(Bucket=etl_bucket, Key=WorkerKey.LOAD, Body=EMPTY_JSON_DATA)
    s3_client.delete_object(Bucket=etl_bucket, Key=initial_trigger_key)
    s3_client.delete_object(Bucket=etl_bucket, Key=final_trigger_key)
    s3_client.delete_object(Bucket=etl_bucket, Key=CHANGELOG_NUMBER)

    # Trigger the bulk load
    s3_client.put_object(
        Bucket=etl_bucket, Key=initial_trigger_key, Body=GOOD_SDS_RECORD.encode()
    )

    trigger_key_deleted = False
    trigger_key_moved_to_history = False
    changelog_number_updated = False
    state_machine_successful = False
    while not all(
        (
            trigger_key_deleted,
            trigger_key_moved_to_history,
            changelog_number_updated,
            state_machine_successful,
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

    # Confirm the final state
    assert trigger_key_deleted
    assert trigger_key_moved_to_history
    assert changelog_number_updated
    assert state_machine_successful