import os
from collections import deque
from datetime import datetime, timezone
from typing import Callable, Generator
from unittest import mock
from uuid import UUID

import pytest
from domain.core.compression import pkl_loads_gzip
from domain.core.device.v2 import Device, DeviceCreatedEvent, DeviceType
from domain.core.device_key.v2 import DeviceKeyType
from domain.repository.device_repository.v2 import DeviceRepository
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


BAD_DEVICE = {}
GOOD_DEVICE_1 = {
    "id": str(UUID(int=1)),
    "name": "device-1",
    "device_type": "product",
    "product_team_id": str(UUID(int=1)),
    "ods_code": "ABC",
    "status": "active",
    "created_on": datetime.now(timezone.utc),
    "updated_on": None,
    "deleted_on": None,
}
GOOD_DEVICE_2 = {
    "id": str(UUID(int=2)),
    "name": "device-1",
    "type": "product",
    "product_team_id": str(UUID(int=2)),
    "ods_code": "ABC",
    "status": "active",
    "created_on": datetime.now(timezone.utc),
    "updated_on": None,
    "deleted_on": None,
}


class MockDeviceRepository(DeviceRepository):
    def all_devices(self) -> Generator[Device, None, None]:
        response = self.client.scan(TableName=self.table_name)
        items = map(unmarshall, response["Items"])
        devices = list(TableKeys.DEVICE.filter(items, key="sk"))
        for device in devices:
            if not device.get("root"):
                continue
            device["tags"] = pkl_loads_gzip(device["tags"])
            yield Device(**device)

    def count(self, by: DeviceType | DeviceKeyType):
        return sum(
            (
                device.device_type is by
                if isinstance(by, DeviceType)
                else any(key.key_type is by for key in device.keys)
            )
            for device in self.all_devices()
        )

    def read_inactive(self, *key_parts):
        # Update this function after PI-XXX is implemented
        return self.read(*key_parts)


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
        device_type=DeviceType.PRODUCT,
        product_team_id=UUID(int=1),
        ods_code=ods_code,
    )
    event = DeviceCreatedEvent(**device.dict())
    device.add_event(event)
    device.add_key(
        key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value=f"{ods_code}:{id}"
    )
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
    initial_unprocessed_data = [
        device_factory(id=i + 1) for i in range(n_initial_unprocessed)
    ]
    initial_processed_data = [
        device_factory(id=(i + 1) * 1000) for i in range(n_initial_processed)
    ]
    put_object(
        key=WorkerKey.LOAD,
        body=pkl_dumps_lz4(deque(map(Device.state, initial_unprocessed_data))),
    )
    repository.write_bulk(map(Device.state, initial_processed_data))

    # Execute the load worker
    response = load.handler(event={"etl_type": "bulk"}, context=None)
    assert response == {
        "stage_name": "load_bulk",
        "processed_records": n_initial_unprocessed,
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

    from etl.sds.worker.load import load

    # Initial state
    initial_unprocessed_data = [
        device_factory(id=i + 1) for i in range(n_initial_unprocessed)
    ]
    initial_processed_data = [
        device_factory(id=(i + 1) * 1000) for i in range(n_initial_processed)
    ]
    put_object(
        key=WorkerKey.LOAD,
        body=pkl_dumps_lz4(deque(map(Device.state, initial_unprocessed_data))),
    )
    repository.write_bulk(map(Device.state, initial_processed_data))

    n_unprocessed_records = len(initial_unprocessed_data)
    while n_unprocessed_records > 0:
        n_processed_records_expected = min(n_unprocessed_records, MAX_RECORDS)
        n_unprocessed_records_expected = (
            n_unprocessed_records - n_processed_records_expected
        )

        # Execute the load worker
        response = load.handler(
            event={"max_records": MAX_RECORDS, "etl_type": "bulk"}, context=None
        )
        assert response == {
            "stage_name": "load_bulk",
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
