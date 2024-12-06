import os
from collections import deque
from typing import Callable
from unittest import mock

import pytest
from domain.core.device import Device
from etl.sds.worker.load_bulk.tests.test_load_bulk_worker import (
    BUCKET_NAME,
    TABLE_NAME,
    MockDeviceRepository,
    device_factory,
)
from etl.sds.worker.transform_update.utils import export_events
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from moto import mock_aws
from mypy_boto3_s3 import S3Client

from test_helpers.dynamodb import mock_table


@pytest.fixture
def mock_s3_client():
    with mock_aws(), mock.patch.dict(
        os.environ,
        {
            "ETL_BUCKET": BUCKET_NAME,
            "TABLE_NAME": TABLE_NAME,
            "AWS_DEFAULT_REGION": "us-east-1",
        },
        clear=True,
    ):
        from etl.sds.worker.load_update import load_update

        load_update.CACHE.S3_CLIENT.create_bucket(Bucket=BUCKET_NAME)
        yield load_update.CACHE.S3_CLIENT


@pytest.fixture
def put_object(mock_s3_client: S3Client):
    return lambda key, body: (
        mock_s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=body)
    )


@pytest.fixture
def get_object(mock_s3_client: S3Client) -> bytes:
    return lambda key: (
        mock_s3_client.get_object(Bucket=BUCKET_NAME, Key=key)["Body"].read()
    )


@pytest.fixture
def repository():
    with mock_table(TABLE_NAME) as dynamodb_client:
        yield MockDeviceRepository(
            table_name=TABLE_NAME, dynamodb_client=dynamodb_client
        )


@pytest.mark.parametrize(
    ("n_initial_unprocessed", "n_initial_processed"),
    [(0, 10), (5, 5), (10, 0)],
    ids=["processed-only", "partly-processed", "unprocessed-only"],
)
def test_load_worker_pass(
    n_initial_unprocessed: int,
    n_initial_processed: int,
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
    repository: MockDeviceRepository,
):
    from etl.sds.worker.load_update import load_update

    # Initial state
    initial_unprocessed_data = [
        device_factory(id=i + 1) for i in range(n_initial_unprocessed)
    ]
    initial_processed_data = [
        device_factory(id=(i + 1) * 1000) for i in range(n_initial_processed)
    ]
    put_object(
        key=WorkerKey.LOAD,
        body=pkl_dumps_lz4(deque(export_events(initial_unprocessed_data))),
    )
    for _device in initial_processed_data:
        repository.write(_device)

    # Execute the load worker
    response = load_update.handler(event={}, context=None)
    assert response == {
        "stage_name": "load",
        "processed_records": 2 * n_initial_unprocessed,
        "unprocessed_records": 0,
        "error_message": None,
    }

    # Final state
    final_unprocessed_data = pkl_loads_lz4(get_object(key=WorkerKey.LOAD))
    final_processed_data: list[Device] = list(repository.all_devices())

    initial_ids = sorted(
        device.id for device in initial_unprocessed_data + initial_processed_data
    )
    final_processed_ids = sorted(device.id for device in final_processed_data)

    # Confirm that everything has now been processed, and that there is no
    # unprocessed data left in the bucket
    assert final_processed_ids == initial_ids
    assert final_unprocessed_data == deque([])


@pytest.mark.parametrize(
    ("n_initial_unprocessed", "n_initial_processed"),
    [(0, 10), (5, 5), (10, 0)],
    ids=["processed-only", "partly-processed", "unprocessed-only"],
)
def test_load_worker_pass_max_records(
    n_initial_unprocessed: int,
    n_initial_processed: int,
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
    repository: MockDeviceRepository,
):
    MAX_RECORDS = 7

    from etl.sds.worker.load_update import load_update

    # Initial state
    initial_unprocessed_data = [
        device_factory(id=i + 1) for i in range(n_initial_unprocessed)
    ]
    initial_processed_data = [
        device_factory(id=(i + 1) * 1000) for i in range(n_initial_processed)
    ]
    _initial_unprocessed_data = deque(export_events(initial_unprocessed_data))
    put_object(
        key=WorkerKey.LOAD,
        body=pkl_dumps_lz4(_initial_unprocessed_data),
    )
    for _device in initial_processed_data:
        repository.write(_device)

    n_unprocessed_records = len(_initial_unprocessed_data)
    while n_unprocessed_records > 0:
        n_processed_records_expected = min(n_unprocessed_records, MAX_RECORDS)
        n_unprocessed_records_expected = (
            n_unprocessed_records - n_processed_records_expected
        )

        # Execute the load worker
        response = load_update.handler(
            event={
                "max_records": MAX_RECORDS,
            },
            context=None,
        )
        assert response == {
            "stage_name": "load",
            "processed_records": n_processed_records_expected,
            "unprocessed_records": n_unprocessed_records_expected,
            "error_message": None,
        }

        n_unprocessed_records = response["unprocessed_records"]

    # Final state
    final_unprocessed_data = pkl_loads_lz4(get_object(key=WorkerKey.LOAD))
    final_processed_data: list[Device] = list(repository.all_devices())

    initial_ids = sorted(
        device.id for device in initial_unprocessed_data + initial_processed_data
    )
    final_processed_ids = sorted(device.id for device in final_processed_data)

    # Confirm that everything has now been processed, and that there is no
    # unprocessed data left in the bucket
    assert final_processed_ids == initial_ids
    assert final_unprocessed_data == deque([])
