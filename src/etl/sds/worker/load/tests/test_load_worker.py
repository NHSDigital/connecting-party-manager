import os
from collections import deque
from itertools import chain, permutations
from typing import Callable, Generator
from unittest import mock
from uuid import UUID

import pytest
from domain.core.aggregate_root import AggregateRoot
from domain.core.device import Device, DeviceCreatedEvent, DeviceType
from domain.core.device_key import DeviceKeyType
from domain.repository.device_repository import DeviceRepository
from domain.repository.keys import TableKeys
from domain.repository.marshall import unmarshall
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from moto import mock_aws
from mypy_boto3_s3 import S3Client

from test_helpers.dynamodb import mock_table

BUCKET_NAME = "my-bucket"
TABLE_NAME = "my-table"


BAD_CPM_EVENT = {}
GOOD_CPM_EVENT_1 = {
    "device_created_event": {
        "id": str(UUID(int=1)),
        "name": "device-1",
        "type": "product",
        "product_team_id": str(UUID(int=1)),
        "ods_code": "ABC",
        "status": "active",
        "deleted_on": None,
    }
}
GOOD_CPM_EVENT_2 = {
    "device_created_event": {
        "id": str(UUID(int=2)),
        "name": "device-1",
        "type": "product",
        "product_team_id": str(UUID(int=2)),
        "ods_code": "ABC",
        "status": "active",
        "deleted_on": None,
    }
}


class MockDeviceRepository(DeviceRepository):
    def all_devices(self) -> Generator[Device, None, None]:
        response = self.client.scan(TableName=self.table_name)
        items = map(unmarshall, response["Items"])
        devices = list(TableKeys.DEVICE.filter(items, key="sk"))
        yield from (Device(**device) for device in devices)

    def count(self, by: DeviceType | DeviceKeyType):
        query = lambda kwargs: (
            self.query_by_key_type(key_type=by, Select="COUNT", **kwargs)
            if isinstance(by, DeviceKeyType)
            else self.query_by_device_type(type=by, Select="COUNT", **kwargs)
        )
        count = 0
        scanning = True
        last_evaluated_key = None
        while scanning:
            response = query(
                kwargs=(
                    {"ExclusiveStartKey": last_evaluated_key}
                    if last_evaluated_key
                    else {}
                )
            )
            count += response["Count"]
            last_evaluated_key = response.get("LastEvaluatedKey")
            scanning = last_evaluated_key is not None

        return count


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
        from etl.sds.worker.load import load

        load.S3_CLIENT.create_bucket(Bucket=BUCKET_NAME)
        yield load.S3_CLIENT


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


def device_factory(id: int) -> Device:
    ods_code = "ABC"
    device = Device(
        id=UUID(int=id),
        name=f"device-{id}",
        type=DeviceType.PRODUCT,
        product_team_id=UUID(int=1),
        ods_code=ods_code,
    )
    print(f"DEVICE {id}", device)  # noqa:T201
    event = DeviceCreatedEvent(**device.dict())
    device.add_event(event)
    device.add_key(type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key=f"{ods_code}:{id}")
    return device


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
    from etl.sds.worker.load import load

    # Initial state
    _initial_unprocessed_data = [
        device_factory(id=i + 1) for i in range(n_initial_unprocessed)
    ]
    initial_unprocessed_data = deque()
    for device in _initial_unprocessed_data:
        initial_unprocessed_data += device.export_events()

    initial_processed_data = [
        device_factory(id=(i + 1) * 1000) for i in range(n_initial_processed)
    ]

    put_object(key=WorkerKey.LOAD, body=pkl_dumps_lz4(initial_unprocessed_data))
    for device in initial_processed_data:
        repository.write(device)

    # Execute the load worker
    response = load.handler(event=None, context=None)
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
        device.id for device in _initial_unprocessed_data + initial_processed_data
    )
    final_processed_ids = sorted(device.id for device in final_processed_data)

    # Confirm that everything has now been processed, and that there is no
    # unprocessed data left in the bucket
    assert final_processed_ids == initial_ids
    assert final_unprocessed_data == deque([])


@pytest.mark.slow
@pytest.mark.parametrize(
    "initial_unprocessed_data",
    permutations([BAD_CPM_EVENT, GOOD_CPM_EVENT_1, GOOD_CPM_EVENT_2]),
)
def test_load_worker_bad_record(
    initial_unprocessed_data: str,
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
    repository: DeviceRepository,
):
    from etl.sds.worker.load import load

    # Initial state
    bad_record_index = initial_unprocessed_data.index(BAD_CPM_EVENT)
    n_initial_unprocessed = len(initial_unprocessed_data)
    put_object(key=WorkerKey.LOAD, body=pkl_dumps_lz4(deque(initial_unprocessed_data)))

    n_initial_processed = 1000
    repository.write(
        AggregateRoot(
            events=list(
                chain.from_iterable(
                    device_factory(id=(i + 1) * 1000).events
                    for i in range(n_initial_processed)
                )
            )
        )
    )

    # Execute the load worker
    response = load.handler(event=None, context=None)
    assert response == {
        "stage_name": "load",
        "processed_records": bad_record_index,
        "unprocessed_records": n_initial_unprocessed - bad_record_index,
        "error_message": (
            "The following errors were encountered\n"
            "  -- Error 1 (ValueError) --\n"
            f"  Failed to parse record {bad_record_index}\n"
            "  {}\n"
            "  not enough values to unpack (expected 1, got 0)"
        ),
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.LOAD)
    final_processed_data: list[Device] = list(repository.all_devices())
    n_final_unprocessed = len(pkl_loads_lz4(final_unprocessed_data))
    n_final_processed = len(final_processed_data)

    # Confirm that there are still unprocessed records, and that there may have been
    # some records processed successfully
    assert n_final_unprocessed > 0
    assert n_final_processed == n_initial_processed + bad_record_index
    assert n_final_unprocessed == n_initial_unprocessed - bad_record_index
