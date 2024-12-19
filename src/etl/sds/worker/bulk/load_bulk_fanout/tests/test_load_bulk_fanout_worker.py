import os
from collections import deque
from pathlib import Path
from typing import Callable
from unittest import mock

import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.product_team.v1 import ProductTeam
from domain.repository.compression import pkl_loads_gzip
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from event.json import json_load
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from sds.epr.bulk_create.bulk_load_fanout import count_indexes

from etl.sds.worker.bulk.tests.test_bulk_e2e import PATH_TO_STAGE_DATA

BUCKET_NAME = "my-bucket"
TABLE_NAME = "my-table"
PATH_TO_HERE = Path(__file__).parent


@pytest.fixture
def mock_s3_client():
    with (
        mock_aws(),
        mock.patch.dict(
            os.environ,
            {
                "ETL_BUCKET": BUCKET_NAME,
                "TABLE_NAME": TABLE_NAME,
                "AWS_DEFAULT_REGION": "us-east-1",
            },
            clear=True,
        ),
    ):
        from etl.sds.worker.bulk.load_bulk import load_bulk

        load_bulk.CACHE.S3_CLIENT.create_bucket(Bucket=BUCKET_NAME)
        yield load_bulk.CACHE.S3_CLIENT


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


def decompress(obj: dict) -> dict:
    tags = obj["PutRequest"]["Item"].get("tags")
    if tags:
        tags["S"] = [pkl_loads_gzip(tag) for tag in pkl_loads_gzip(tags["S"])]

    questionnaire_responses = obj["PutRequest"]["Item"].get(
        "questionnaire_responses", {}
    )
    if questionnaire_responses.get("S"):
        questionnaire_responses["S"] = pkl_loads_gzip(questionnaire_responses["S"])

    return obj


def test_load_worker_fanout(
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
):
    _EACH_FANOUT_BATCH_SIZE = 10
    from etl.sds.worker.bulk.load_bulk_fanout import load_bulk_fanout

    load_bulk_fanout.EACH_FANOUT_BATCH_SIZE = _EACH_FANOUT_BATCH_SIZE

    # Initial state
    with open(PATH_TO_STAGE_DATA / "2.transform_output.json") as f:
        input_data: list[dict[str, dict]] = json_load(f)

    put_object(
        key=WorkerKey.LOAD,
        body=pkl_dumps_lz4(deque(input_data)),
    )

    # Execute the load worker
    responses = load_bulk_fanout.handler(event={}, context=None)

    *head_responses, tail_response = responses

    assert len(head_responses) > 1

    expected_head_responses = [
        {
            "stage_name": "load_bulk_fanout",
            "processed_records": _EACH_FANOUT_BATCH_SIZE,
            "unprocessed_records": 0,
            "s3_input_path": f"s3://my-bucket/input--load/unprocessed.{i}",
            "error_message": None,
        }
        for i in range(len(head_responses))
    ]
    assert head_responses == expected_head_responses

    tail_processed_records = tail_response.pop("processed_records")
    assert tail_processed_records <= _EACH_FANOUT_BATCH_SIZE
    assert tail_response == {
        "stage_name": "load_bulk_fanout",
        "unprocessed_records": 0,
        "s3_input_path": f"s3://my-bucket/input--load/unprocessed.{len(head_responses)}",
        "error_message": None,
    }

    # Final state
    final_processed_data = pkl_loads_lz4(get_object(key=WorkerKey.LOAD))
    assert final_processed_data == deque([])
    total_size = 0
    for i in range(_EACH_FANOUT_BATCH_SIZE):
        final_unprocessed_data = pkl_loads_lz4(get_object(key=f"{WorkerKey.LOAD}.{i}"))
        assert isinstance(final_unprocessed_data, deque)
        total_size += len(final_unprocessed_data)

        with open(PATH_TO_STAGE_DATA / f"3.load_fanout_output.{i}.json") as f:
            expected_final_data: list[dict[str, dict]] = json_load(f)
        assert list(map(decompress, final_unprocessed_data)) == list(
            map(decompress, expected_final_data)
        )

    expected_total_size = 0
    for obj in input_data:
        ((obj_name, obj_data),) = obj.items()
        match obj_name:
            case "Device":
                obj = Device(**obj_data)
            case "DeviceReferenceData":
                obj = DeviceReferenceData(**obj_data)
            case "ProductTeam":
                obj = ProductTeam(**obj_data)
            case "CpmProduct":
                obj = CpmProduct(**obj_data)
        expected_total_size += count_indexes(obj)

    assert total_size == expected_total_size

    total_processed_records_from_response = (
        tail_processed_records + _EACH_FANOUT_BATCH_SIZE * len(head_responses)
    )
    assert total_size == total_processed_records_from_response
