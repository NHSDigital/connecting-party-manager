import os
from collections import deque
from itertools import chain
from pathlib import Path
from typing import Callable
from unittest import mock

import pytest
from domain.core.enum import Environment
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dumps_lz4
from event.json import json_load
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from sds.epr.utils import is_as_device, is_mhs_device

from etl.sds.worker.update.tests.test_update_e2e import PATH_TO_STAGE_DATA
from test_helpers.dynamodb import mock_table

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
        from etl.sds.worker.update.load_update import load_update

        load_update.CACHE.S3_CLIENT.create_bucket(Bucket=BUCKET_NAME)
        yield load_update.CACHE.S3_CLIENT


@pytest.fixture
def put_object(mock_s3_client: S3Client):
    return lambda key, body: (
        mock_s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=body)
    )


def test_load_worker_pass(put_object: Callable[[str], None]):
    from etl.sds.worker.update.load_update import load_update

    # Initial state
    with open(PATH_TO_STAGE_DATA / f"2.transform_output.json") as f:
        input_data = json_load(f)

    put_object(
        key=WorkerKey.LOAD,
        body=pkl_dumps_lz4(deque(input_data)),
    )

    # Execute the load worker
    with mock_table(TABLE_NAME) as dynamodb_client:
        load_update.CACHE.REPOSITORY.client = dynamodb_client

        response = load_update.handler(
            event={"s3_input_path": f"s3://{BUCKET_NAME}/{WorkerKey.LOAD}"},
            context=None,
        )

        assert response == {
            "stage_name": "load",
            "processed_records": len(input_data),
            "unprocessed_records": 0,
            "error_message": None,
        }

        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=dynamodb_client
        )
        (product_team,) = product_team_repo.search()
        product_team_by_key = product_team_repo.read("EPR-LSP04")
        product_team_by_id = product_team_repo.read(
            "LSP04.d2440e42-ce71-47ea-b1e1-d7f3a2bf42aa"
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
        assert products == [product_team_a]

        device_repo = DeviceRepository(
            table_name=TABLE_NAME, dynamodb_client=dynamodb_client
        )
        devices = list(
            chain.from_iterable(
                device_repo.search(
                    product_team_id=product_team.id,
                    product_id=product.id,
                    environment=Environment.PROD,
                )
                for product in products
            )
        )
        mhs_devices = [d for d in devices if is_mhs_device(d)]
        as_devices = [d for d in devices if is_as_device(d)]
        assert len(devices) == len(mhs_devices) + len(as_devices)
        assert len(mhs_devices) == 1
        assert len(as_devices) == 0

        device_ref_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=dynamodb_client
        )
        device_ref_datas = list(
            chain.from_iterable(
                device_ref_data_repo.search(
                    product_team_id=product_team.id,
                    product_id=product.id,
                    environment=Environment.PROD,
                )
                for product in products
            )
        )
        assert len(device_ref_datas) == 1
