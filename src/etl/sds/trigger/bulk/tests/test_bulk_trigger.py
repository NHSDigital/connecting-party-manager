import time
from functools import partial

import boto3
import pytest
from event.aws.client import dynamodb_client

from etl.sds.tests.etl_test_utils.ask_s3 import (
    database_isnt_empty as _database_isnt_empty,
)
from etl.sds.tests.etl_test_utils.ask_s3 import extract_is_empty as _extract_is_empty
from etl.sds.tests.etl_test_utils.ask_s3 import load_is_empty as _load_is_empty
from etl.sds.tests.etl_test_utils.ask_s3 import (
    transform_is_empty as _transform_is_empty,
)
from etl.sds.tests.etl_test_utils.ask_s3 import (
    was_changelog_number_updated as _was_changelog_number_updated,
)
from etl.sds.tests.etl_test_utils.ask_s3 import (
    was_etl_state_lock_removed as _was_etl_state_lock_removed,
)
from etl.sds.tests.etl_test_utils.ask_s3 import (
    was_queue_history_created as _was_queue_history_created,
)
from etl.sds.tests.etl_test_utils.ask_s3 import (
    was_state_machine_history_created as _was_state_machine_history_created,
)
from etl.sds.tests.etl_test_utils.ask_s3 import (
    was_trigger_key_deleted as _was_trigger_key_deleted,
)
from etl.sds.tests.etl_test_utils.etl_state import clear_etl_state, get_etl_config
from etl.sds.worker.bulk.tests.test_bulk_e2e import PATH_TO_STAGE_DATA

EXPECTED_CHANGELOG_NUMBER = 123


def message(x):
    print(x)  # noqa


@pytest.mark.timeout(20)
@pytest.mark.integration
def test_bulk_trigger():
    # Prerequisites
    with open(PATH_TO_STAGE_DATA / "0.extract_input.ldif") as f:
        input_data = f.read().encode()

    etl_config = get_etl_config(f"{EXPECTED_CHANGELOG_NUMBER}.ldif", etl_type="bulk")
    db_client = dynamodb_client()
    s3_client = boto3.client("s3")
    clear_etl_state(s3_client=s3_client, etl_config=etl_config)

    # Define questions
    was_trigger_key_deleted = partial(
        _was_trigger_key_deleted, s3_client=s3_client, etl_config=etl_config
    )
    was_queue_history_created = partial(
        _was_queue_history_created,
        s3_client=s3_client,
        etl_config=etl_config,
        expected_content=input_data,
    )
    was_state_machine_history_created = partial(
        _was_state_machine_history_created,
        s3_client=s3_client,
        etl_config=etl_config,
        expected_content=input_data,
    )
    was_changelog_number_updated = partial(
        _was_changelog_number_updated, s3_client=s3_client, bucket=etl_config.bucket
    )
    extract_is_empty = partial(
        _extract_is_empty, s3_client=s3_client, bucket=etl_config.bucket
    )
    transform_is_empty = partial(
        _transform_is_empty, s3_client=s3_client, bucket=etl_config.bucket
    )
    load_is_empty = partial(
        _load_is_empty, s3_client=s3_client, bucket=etl_config.bucket
    )
    was_state_lock_removed = partial(
        _was_etl_state_lock_removed, s3_client=s3_client, bucket=etl_config.bucket
    )
    database_isnt_empty = partial(
        _database_isnt_empty, db_client=db_client, table_name=etl_config.table_name
    )

    # Trigger the bulk load
    s3_client.put_object(
        Bucket=etl_config.bucket, Key=etl_config.initial_trigger_key, Body=input_data
    )

    # Sign-off through the expected lifecycle of the bulk ETL
    while not was_trigger_key_deleted():
        time.sleep(5)
    message("Trigger key deleted")

    while not was_queue_history_created():
        time.sleep(5)
    message("Queue history created")

    while not was_state_machine_history_created():
        time.sleep(5)
    message("State machine history created")

    while not was_changelog_number_updated():
        time.sleep(5)
    message("Changelog number updated")

    while not extract_is_empty():
        time.sleep(5)
    message("Extract's input data is now in empty state")

    while not transform_is_empty():
        time.sleep(5)
    message("Transform's input data is now in empty state")

    while not load_is_empty():
        time.sleep(5)
    message("Load's input data is now in empty state")

    assert database_isnt_empty()
    message("Database isn't empty")

    while not was_state_lock_removed():
        message("State lock has been removed")
        time.sleep(5)
