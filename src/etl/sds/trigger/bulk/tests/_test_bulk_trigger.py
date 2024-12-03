import time
from collections import deque
from functools import partial

import boto3
import pytest
from domain.core.device import DeviceType
from etl.sds.worker.extract.tests.test_extract_worker import GOOD_SDS_RECORD
from etl.sds.worker.load_bulk.tests._test_load_bulk_worker import MockDeviceRepository
from etl_utils.constants import CHANGELOG_NUMBER, ETL_STATE_LOCK, WorkerKey
from etl_utils.io.test.io_utils import pkl_loads_lz4
from event.aws.client import dynamodb_client
from event.json import json_loads

from etl.sds.trigger.bulk.tests.etl_test_utils.etl_state import (
    ask_s3,
    ask_s3_prefix,
    clear_etl_state,
    get_etl_config,
)
from test_helpers.dynamodb import clear_dynamodb_table

EXPECTED_CHANGELOG_NUMBER = 123


@pytest.mark.timeout(20)
@pytest.mark.integration
def test_bulk_trigger():
    # Where the state is located
    bucket_config = get_etl_config()
    table_name = bucket_config["table_name"]

    client = dynamodb_client()
    repository = MockDeviceRepository(table_name=table_name, dynamodb_client=client)

    s3_client = boto3.client("s3")
    ask_s3 = partial(ask_s3, s3_client=s3_client, bucket=bucket_config["etl_bucket"])
    ask_s3_prefix = partial(
        ask_s3_prefix, s3_client=s3_client, bucket=bucket_config["etl_bucket"]
    )

    was_trigger_key_deleted = lambda: not ask_s3(
        key=bucket_config["initial_trigger_key"]
    )
    was_queue_history_created = lambda: ask_s3_prefix(
        key_prefix=f"{bucket_config['queue_history_key_prefix']}/bulk",
        question=lambda x: x == GOOD_SDS_RECORD.encode(),
    )
    was_state_machine_history_created = lambda: ask_s3_prefix(
        key_prefix=f"{bucket_config['state_machine_history_key_prefix']}/bulk",
        question=lambda x: x == GOOD_SDS_RECORD.encode(),
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

    clear_etl_state(s3_client=s3_client, bucket_config=bucket_config)
    s3_client.delete_object(Bucket=bucket_config["etl_bucket"], Key=CHANGELOG_NUMBER)
    s3_client.delete_object(Bucket=bucket_config["etl_bucket"], Key=ETL_STATE_LOCK)
    clear_dynamodb_table(client=client, table_name=bucket_config["table_name"])

    # Trigger the bulk load
    s3_client.put_object(
        Bucket=bucket_config["etl_bucket"],
        Key=bucket_config["initial_trigger_key"],
        Body=GOOD_SDS_RECORD.encode(),
    )

    trigger_key_deleted = False
    queue_history_created = False
    state_machine_history_created = False
    changelog_number_updated = False
    state_machine_successful = False
    etl_state_lock_removed = False
    while not all(
        (
            trigger_key_deleted,
            queue_history_created,
            state_machine_history_created,
            changelog_number_updated,
            state_machine_successful,
            etl_state_lock_removed,
        )
    ):
        time.sleep(5)
        trigger_key_deleted = trigger_key_deleted or was_trigger_key_deleted()
        queue_history_created = queue_history_created or was_queue_history_created()
        state_machine_history_created = (
            state_machine_history_created or was_state_machine_history_created()
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
    assert queue_history_created
    assert state_machine_history_created
    assert changelog_number_updated
    assert state_machine_successful
    assert etl_state_lock_removed
