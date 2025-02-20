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
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.epr_product.v1 import EprProduct
from domain.core.product_team_epr.v1 import ProductTeam
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
    with (
        mock.patch.dict(os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}, clear=True),
        mock_aws(),
    ):
        client = boto3.client("s3")
        yield client


@pytest.fixture
def scenario(request: pytest.FixtureRequest) -> Scenario:
    scenario_path: Path = request.param
    scenario_name = f"{scenario_path.parent.name}/{scenario_path.name}"

    scenario_config = scenario_path / "__init__.py"
    if not scenario_config.exists():
        pytest.skip(f"No config found at{scenario_config}")

    spec = spec_from_file_location(scenario_name, str(scenario_config))
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
    os.environ["TABLE_NAME"] = read_terraform_output("dynamodb_epr_table_name.value")

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
    os.environ["TABLE_NAME"] = read_terraform_output("dynamodb_epr_table_name.value")

    from etl.sds.worker.update.load_update import load_update

    yield load_update.handler
    os.environ = original_environ


def make_hashable(data):
    """
    Recursively convert lists and other unhashable types in a dictionary to hashable equivalents.
    """
    if isinstance(data, list):
        return tuple(sorted(make_hashable(item) for item in data))
    elif isinstance(data, dict):
        return frozenset((key, make_hashable(value)) for key, value in data.items())
    return data


def equivalent_questionnaire_responses[
    item_type: Device | DeviceReferenceData
](new_item: item_type, old_item: item_type) -> bool:
    # Check if the keys (questionnaire IDs) match
    questionnaires = old_item.questionnaire_responses.keys()
    assert new_item.questionnaire_responses.keys() == questionnaires

    # Compare the questionnaire responses for each questionnaire ID
    for q in questionnaires:
        new_questionnaire_responses = new_item.questionnaire_responses[q]
        old_questionnaire_responses = old_item.questionnaire_responses[q]

        assert len(new_questionnaire_responses) == len(old_questionnaire_responses)

        # Compare the responses as unordered collections
        new_data_set = {make_hashable(qr.data) for qr in new_questionnaire_responses}
        old_data_set = {make_hashable(qr.data) for qr in old_questionnaire_responses}

        assert new_data_set == old_data_set

    return True


def equivalent_with_unordered_lists[
    item_type: ProductTeam | EprProduct | Device | DeviceReferenceData
](new_item: item_type, old_item: item_type) -> bool:
    assert new_item.id != old_item.id
    assert new_item.name == old_item.name
    assert new_item.created_on > old_item.created_on
    if old_item.updated_on:
        assert new_item.updated_on is not None
        assert new_item.updated_on > old_item.updated_on

    # Check `keys` field for non-DeviceReferenceData items
    if not isinstance(old_item, DeviceReferenceData):
        assert new_item.keys == old_item.keys

    # Handle `questionnaire_responses` equivalence for Devices and DeviceReferenceData
    if isinstance(old_item, (Device, DeviceReferenceData)):
        assert equivalent_questionnaire_responses(new_item=new_item, old_item=old_item)

    # Handle additional fields specific to Device
    if isinstance(old_item, Device):
        assert set(new_item.tags) == set(old_item.tags)

        # Compare device_reference_data.values() field as unordered collections
        new_data = list(new_item.device_reference_data.values())
        old_data = list(old_item.device_reference_data.values())
        # Make elements hashable before comparing as sets
        new_data_hashable = {make_hashable(item) for item in new_data}
        old_data_hashable = {make_hashable(item) for item in old_data}
        assert new_data_hashable == old_data_hashable

    return True
