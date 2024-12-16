import json
import os
from collections import deque
from itertools import chain
from pathlib import Path
from typing import Callable
from unittest import mock

import boto3
import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.product_team.v1 import ProductTeam
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dumps_lz4, pkl_load_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from event.json import json_load
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from sds.epr.bulk_create.bulk_load_fanout import FANOUT
from sds.epr.utils import is_as_device, is_mhs_device

from etl.sds.worker.bulk.tests.test_bulk_e2e import PATH_TO_STAGE_DATA
from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output

BUCKET_NAME = "my-bucket"
TABLE_NAME = "my-table"
PATH_TO_HERE = Path(__file__).parent


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


def test_load_worker_pass(
    put_object: Callable[[str], None], get_object: Callable[[str], bytes]
):
    from etl.sds.worker.bulk.load_bulk import load_bulk

    # Initial state
    for i in range(FANOUT):
        with open(PATH_TO_STAGE_DATA / f"3.load_fanout_output.{i}.json") as f:
            input_data = json_load(f)

        put_object(
            key=f"{WorkerKey.LOAD}.{i}",
            body=pkl_dumps_lz4(deque(input_data)),
        )

    # Execute the load worker
    with mock_table(TABLE_NAME) as dynamodb_client:
        load_bulk.CACHE.REPOSITORY.client = dynamodb_client

        responses = []
        for i in range(FANOUT):
            response = load_bulk.handler(
                event={"s3_input_path": f"s3://{BUCKET_NAME}/{WorkerKey.LOAD}.{i}"},
                context=None,
            )
            responses.append(response)

            # Final state
            final_unprocessed_data = pkl_loads_lz4(
                get_object(key=f"{WorkerKey.LOAD}.{i}")
            )
            assert final_unprocessed_data == deque([])

        assert responses == [
            {
                "stage_name": "load",
                "processed_records": 10,
                "unprocessed_records": 0,
                "error_message": None,
            }
        ] * (FANOUT - 1) + [
            {
                "stage_name": "load",
                "processed_records": 7,
                "unprocessed_records": 0,
                "error_message": None,
            }
        ]
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=dynamodb_client
        )
        (product_team,) = product_team_repo.search()
        product_team_by_key = product_team_repo.read("EPR-LSP04")
        product_team_by_id = product_team_repo.read(
            "LSP04.ec12b569-ea31-4c28-9559-17d533c78441"
        )
        assert product_team == product_team_by_key
        assert product_team == product_team_by_id

        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=dynamodb_client
        )
        products = product_repo.search(product_team_id=product_team.id)
        product_team_a = product_repo.read(
            product_team_id=product_team.id, id="AAA-111111"
        )
        product_team_b = product_repo.read(
            product_team_id=product_team.id, id="BBB-111111"
        )
        assert products == [product_team_b, product_team_a]

        device_repo = DeviceRepository(
            table_name=TABLE_NAME, dynamodb_client=dynamodb_client
        )
        devices = list(
            chain.from_iterable(
                device_repo.search(
                    product_team_id=product_team.id, product_id=product.id
                )
                for product in products
            )
        )
        mhs_devices = [d for d in devices if is_mhs_device(d)]
        as_devices = [d for d in devices if is_as_device(d)]
        assert len(devices) == len(mhs_devices) + len(as_devices)
        assert len(mhs_devices) == 2
        assert len(as_devices) == 4

        device_ref_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=dynamodb_client
        )
        device_ref_datas = list(
            chain.from_iterable(
                device_ref_data_repo.search(
                    product_team_id=product_team.id, product_id=product.id
                )
                for product in products
            )
        )
        assert len(device_ref_datas) == 4

    with open(PATH_TO_STAGE_DATA / "2.transform_output.json") as f:
        input_data: list[dict[str, dict]] = json_load(f)

    (input_product_team,) = (
        ProductTeam(**data)
        for item in input_data
        for object_type_name, data in item.items()
        if object_type_name == "ProductTeam"
    )

    input_products = sorted(
        (
            CpmProduct(**data)
            for item in input_data
            for object_type_name, data in item.items()
            if object_type_name == "CpmProduct"
        ),
        key=lambda product: str(product.id),
    )

    input_devices = sorted(
        (
            Device(**data)
            for item in input_data
            for object_type_name, data in item.items()
            if object_type_name == "Device"
        ),
        key=lambda device: (str(device.product_id), device.id),
    )

    input_device_ref_data = sorted(
        (
            DeviceReferenceData(**data)
            for item in input_data
            for object_type_name, data in item.items()
            if object_type_name == "DeviceReferenceData"
        ),
        key=lambda device_ref_data: (
            str(device_ref_data.product_id),
            device_ref_data.id,
        ),
    )

    assert product_team == input_product_team
    assert products == input_products
    assert devices == input_devices
    assert device_ref_datas == input_device_ref_data


@pytest.mark.integration
@pytest.mark.parametrize("path", (PATH_TO_HERE / "edge_cases").iterdir())
def test_load_worker_edge_cases(path: Path):
    if path.name == ".gitkeep":
        pytest.skip()

    s3_client = boto3.client("s3")
    lambda_client = boto3.client("lambda")
    bucket = read_terraform_output("sds_etl.value.bucket")
    lambda_name = read_terraform_output("sds_etl.value.bulk_load_lambda_arn")

    with open(path) as f:
        s3_client.put_object(
            Key=f"{WorkerKey.LOAD}.0",
            Bucket=bucket,
            body=pkl_dumps_lz4(deque(json_load(f))),
        )

    response = lambda_client.invoke(
        FunctionName=lambda_name,
        Payload=json.dumps({"s3_input_path": f"s3://{BUCKET_NAME}/{WorkerKey.LOAD}.0"}),
    )
    assert json_load(response["Payload"]) == {
        "stage_name": "load",
        "processed_records": 10,
        "unprocessed_records": 0,
        "error_message": None,
    }

    # Final state
    _final_unprocessed_data = s3_client.get_object(
        Key=f"{WorkerKey.LOAD}.0", Bucket=bucket
    )["Body"]
    final_unprocessed_data = pkl_load_lz4(_final_unprocessed_data)
    assert final_unprocessed_data == deque([])
