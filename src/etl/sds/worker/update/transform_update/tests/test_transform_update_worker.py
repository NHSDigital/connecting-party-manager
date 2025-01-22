import datetime
import json
import os
from collections import deque
from pathlib import Path
from typing import Callable
from unittest import mock
from uuid import UUID

import pytest
from domain.core.enum import Environment
from domain.core.root import Root
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from event.json import json_load, json_loads
from moto import mock_aws
from mypy_boto3_s3 import S3Client

from etl.sds.worker.bulk.transform_bulk.tests.test_transform_bulk_worker import (
    _assert_domain_object_equal,
)
from etl.sds.worker.update.tests.test_update_e2e import PATH_TO_STAGE_DATA
from etl.sds.worker.update.transform_update.utils import export_events
from test_helpers.dynamodb import mock_table

BUCKET_NAME = "my-bucket"
TABLE_NAME = "my-table"
PATH_TO_HERE = Path(__file__).parent


@pytest.fixture
def mock_s3_client():
    with mock_aws(), mock_table(TABLE_NAME) as dynamodb_client, mock.patch.dict(
        os.environ,
        {
            "ETL_BUCKET": BUCKET_NAME,
            "TABLE_NAME": TABLE_NAME,
            "AWS_DEFAULT_REGION": "us-east-1",
        },
        clear=True,
    ):
        from etl.sds.worker.update.transform_update import transform_update

        transform_update.S3_CLIENT.create_bucket(Bucket=BUCKET_NAME)
        transform_update.REPOSITORIES["etl_device_repository"].client = dynamodb_client
        transform_update.REPOSITORIES["product_team_repository"].client = (
            dynamodb_client
        )
        transform_update.REPOSITORIES["product_repository"].client = dynamodb_client
        transform_update.REPOSITORIES["device_repository"].client = dynamodb_client
        transform_update.REPOSITORIES["device_reference_data_repository"].client = (
            dynamodb_client
        )
        yield transform_update.S3_CLIENT


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


def json_dumps_event(obj):
    return json.dumps(
        obj,
        default=lambda x: (
            list(x)
            if isinstance(x, (deque, set, tuple))
            else (
                x.isoformat()
                if isinstance(x, datetime.datetime)
                else (str(x) if isinstance(x, UUID) else x)
            )
        ),
    )


def events_are_equivalent(event_1: dict, event_2: dict):
    ((event_type_1, event_data_1),) = event_1.items()
    ((event_type_2, event_data_2),) = event_2.items()

    assert event_type_1 == event_type_2

    _assert_domain_object_equal(event_data_1, event_data_2)

    if "questionnaire_responses" in event_data_1:
        qr_1 = event_data_1["questionnaire_responses"]
        qr_2 = event_data_2["questionnaire_responses"]
        assert qr_2.keys() == qr_1.keys()
        for name in qr_2:
            for r1, r2 in zip(qr_1[name], qr_2[name]):
                _assert_domain_object_equal(r1, r2)
    return True


def test_transform_worker(
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
):

    from etl.sds.worker.update.transform_update import transform_update

    initial_processed_data = deque([])

    # Initial state
    with open(PATH_TO_STAGE_DATA / "1.extract_output.json") as f:
        input_data = deque(json_load(f))

    put_object(key=WorkerKey.TRANSFORM, body=pkl_dumps_lz4(input_data))
    put_object(key=WorkerKey.LOAD, body=pkl_dumps_lz4(initial_processed_data))

    # Execute the transform worker
    response = transform_update.handler(event={}, context=None)

    assert response == {
        "stage_name": "transform",
        "processed_records": 9,
        "unprocessed_records": 0,
        "error_message": None,
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM)
    output_data: str = get_object(key=f"{WorkerKey.LOAD}")
    n_final_unprocessed = len(pkl_loads_lz4(final_unprocessed_data))

    assert n_final_unprocessed == 0

    with open(PATH_TO_STAGE_DATA / "2.transform_output.json") as f:
        template_output: list[dict[str, dict]] = json_load(f)

    _created_objects: list[dict[str, dict]] = pkl_loads_lz4(output_data)
    created_objects = json_loads(json_dumps_event(_created_objects))

    for created_obj, template_obj in zip(created_objects, template_output):
        assert events_are_equivalent(created_obj, template_obj)


def test__export_events():
    org = Root.create_ods_organisation(ods_code="AAA")
    product_team = org.create_product_team_epr(name="abc")
    product = product_team.create_epr_product(name="product")

    devices = []
    for i in range(3):
        device = product.create_device(name=f"device-{i}", environment=Environment.PROD)
        device.add_tag(foo=str(i))
        devices.append(device)
    events = export_events(devices)
    for event in events:
        assert len(event) == 1
    event_names = [list(event.keys())[0] for event in events]
    assert event_names == [
        "device_created_event",
        "device_tag_added_event",
    ] * len(devices)
