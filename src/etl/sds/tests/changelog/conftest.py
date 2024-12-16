import os
import sys
from collections import deque
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Generator
from unittest import mock

import boto3
import pytest
from etl_utils.io import pkl_dumps_lz4
from etl_utils.worker.model import WorkerEnvironment
from moto import mock_aws
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_s3 import S3Client

from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output

from .utils import Scenario

SCENARIO_PATHS = list((Path(__file__).parent.glob("scenarios/*/*")))

TABLE_NAME = "my-table"
ETL_BUCKET = "etl-bucket"


@pytest.fixture
def dynamodb_client() -> Generator[DynamoDBClient, None, None]:
    with mock_table(table_name=TABLE_NAME) as client:
        yield client


@pytest.fixture
def s3_client() -> Generator[S3Client, None, None]:
    with mock.patch.dict(
        os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}, clear=True
    ), mock_aws():
        client = boto3.client("s3")
        yield client


@pytest.fixture
def scenario(request: pytest.FixtureRequest) -> Scenario:
    scenario_path: Path = request.param
    scenario_name = f"{scenario_path.parent.name}/{scenario_path.name}"

    spec = spec_from_file_location(scenario_name, str(scenario_path / "__init__.py"))
    module = module_from_spec(spec)
    sys.modules[scenario_name] = module
    spec.loader.exec_module(module)
    return module.SCENARIO


def parametrize_over_scenarios():
    return pytest.mark.parametrize(
        "scenario",
        SCENARIO_PATHS,
        indirect=True,
        ids=list(map(lambda path: f"{path.parent.name}/{path.name}", SCENARIO_PATHS)),
    )


@pytest.fixture
def extract_handler(scenario: Scenario, s3_client: S3Client):
    s3_client.create_bucket(Bucket=ETL_BUCKET)
    s3_client.put_object(
        Bucket=ETL_BUCKET,
        Key="input--extract/unprocessed",
        Body=scenario.extract_input,
    )
    s3_client.put_object(
        Bucket=ETL_BUCKET,
        Key="input--transform/unprocessed",
        Body=pkl_dumps_lz4(deque()),
    )

    with mock.patch.dict(
        os.environ,
        {"ETL_BUCKET": ETL_BUCKET, "AWS_DEFAULT_REGION": "us-east-1"},
        clear=True,
    ):
        from etl.sds.worker.update.extract_update import extract_update

        extract_update.ENVIRONMENT = WorkerEnvironment.build()
        extract_update.S3_CLIENT = s3_client
        yield extract_update.handler


@pytest.fixture
def transform_handler(scenario: Scenario):
    etl_bucket = read_terraform_output("sds_etl.value.bucket")

    original_environ = deepcopy(os.environ)

    os.environ["ETL_BUCKET"] = etl_bucket
    os.environ["TABLE_NAME"] = read_terraform_output("dynamodb_table_name.value")

    from etl.sds.worker.update.transform_update import transform_update

    transform_update.S3_CLIENT.put_object(
        Bucket=etl_bucket,
        Key="input--transform/unprocessed",
        Body=pkl_dumps_lz4(deque(scenario.extract_output)),
    )
    transform_update.S3_CLIENT.put_object(
        Bucket=etl_bucket,
        Key="input--load/unprocessed",
        Body=pkl_dumps_lz4(deque()),
    )

    yield transform_update.handler

    os.environ = original_environ


@pytest.fixture
def load_handler(scenario: Scenario):
    original_environ = deepcopy(os.environ)

    os.environ["ETL_BUCKET"] = read_terraform_output("sds_etl.value.bucket")
    os.environ["TABLE_NAME"] = read_terraform_output("dynamodb_table_name.value")

    from etl.sds.worker.update.load_update import load_update

    yield load_update.handler
    os.environ = original_environ
