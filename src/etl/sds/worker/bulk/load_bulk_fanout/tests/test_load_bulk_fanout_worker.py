import os
from collections import deque
from itertools import batched
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
from sds.epr.bulk_create.bulk_load_fanout import (
    FANOUT,
    calculate_batch_size,
    count_indexes,
)

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


@pytest.mark.parametrize(
    ("n_batches", "sequence_length", "expected_batch_size", "expected_n_batches"),
    ((4, 100, 25, 4), (3, 100, 34, 3), (16, 30, 2, 15)),
)
def test_calculate_batch_size_general(
    n_batches: int,
    sequence_length: int,
    expected_batch_size: int,
    expected_n_batches: int,
):
    n_batches = n_batches
    sequence = list(range(sequence_length))
    batch_size = calculate_batch_size(sequence, n_batches)
    assert batch_size == expected_batch_size

    batches = list(batched(sequence, batch_size))
    assert len(batches) == expected_n_batches


def test_load_worker_fanout(
    put_object: Callable[[str], None], get_object: Callable[[str], bytes]
):
    from etl.sds.worker.bulk.load_bulk_fanout import load_bulk_fanout

    # Initial state
    with open(PATH_TO_STAGE_DATA / "2.transform_output.json") as f:
        input_data: list[dict[str, dict]] = json_load(f)

    put_object(
        key=WorkerKey.LOAD,
        body=pkl_dumps_lz4(deque(input_data)),
    )

    # Execute the load worker
    responses = load_bulk_fanout.handler(event={}, context=None)

    assert len(responses) == FANOUT
    assert responses == [
        {
            "stage_name": "load_bulk_fanout",
            "processed_records": 10,
            "unprocessed_records": 0,
            "s3_input_path": f"s3://my-bucket/input--load/unprocessed.{i}",
            "error_message": None,
        }
        for i in range(0, FANOUT - 1)
    ] + [
        {
            "stage_name": "load_bulk_fanout",
            "processed_records": 7,
            "unprocessed_records": 0,
            "s3_input_path": f"s3://my-bucket/input--load/unprocessed.{FANOUT - 1}",
            "error_message": None,
        },
    ]

    # Final state
    final_processed_data = pkl_loads_lz4(get_object(key=WorkerKey.LOAD))
    assert final_processed_data == deque([])
    total_size = 0
    for i in range(10):
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
