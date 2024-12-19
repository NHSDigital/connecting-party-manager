import os
from collections import deque
from pathlib import Path
from typing import Callable
from unittest import mock

import pytest
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from event.json import json_load
from moto import mock_aws
from mypy_boto3_s3 import S3Client

from etl.sds.worker.bulk.tests.test_bulk_e2e import PATH_TO_STAGE_DATA
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
        from etl.sds.worker.bulk.transform_bulk import transform_bulk

        transform_bulk.EPR_PRODUCT_TEAM_REPOSITORY.client = dynamodb_client
        transform_bulk.S3_CLIENT.create_bucket(Bucket=BUCKET_NAME)
        yield transform_bulk.S3_CLIENT


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


def _assert_domain_object_equal(a, b):
    for k in a.keys() - {
        "id",
        "product_id",
        "product_team_id",
        "environment",
        "device_reference_data",
        "questionnaire_responses",
        "created_on",
        "updated_on",
        "deleted_on",
        "tags",
    }:
        assert a[k] == b[k], f"{k}: {a[k]} not same as {b[k]}"


def assert_transform_outputs_equal(created_objects, template_output):
    assert len(created_objects) == len(template_output)
    assert all(a.keys() == b.keys() for a, b in zip(created_objects, template_output))

    current_product_id = None
    device_reference_data_ids = None
    for nested_created_item, nested_template_item in zip(
        created_objects, template_output
    ):
        (object_type_name,) = nested_created_item.keys()

        created_item = nested_created_item[object_type_name]
        template_item = nested_template_item[object_type_name]

        if object_type_name == "CpmProduct":
            current_product_id = created_item["id"]
            device_reference_data_ids = []
        elif object_type_name == "DeviceReferenceData":
            device_reference_data_ids.append(created_item["id"])

        # Verify that the product id is internally consistent
        if created_item.get("product_id"):
            assert created_item.get("product_id") == current_product_id

        # Verify that the device reference data ids are internally consistent
        if created_item.get("device_reference_data"):
            assert all(
                id in device_reference_data_ids
                for id in created_item.get("device_reference_data")
            )

        # Check that this object is broadly consistent with the expectation
        assert created_item.keys() == template_item.keys()
        _assert_domain_object_equal(created_item, template_item)

        # Check that any questionnaire responses are broadly consistent with the expectation
        if "questionnaire_responses" in created_item:
            created_questionnaire_response = created_item["questionnaire_responses"]
            template_questionnaire_response = template_item["questionnaire_responses"]
            assert (
                template_questionnaire_response.keys()
                == created_questionnaire_response.keys()
            )
            for questionnaire_name in template_questionnaire_response:
                for created_response, template_response in zip(
                    created_questionnaire_response[questionnaire_name],
                    template_questionnaire_response[questionnaire_name],
                ):
                    _assert_domain_object_equal(created_response, template_response)
    return True


def test_transform_worker(
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
):

    from etl.sds.worker.bulk.transform_bulk import transform_bulk

    initial_processed_data = deque([])

    # Initial state
    with open(PATH_TO_STAGE_DATA / "1.extract_output.json") as f:
        input_data = deque(json_load(f))

    put_object(key=WorkerKey.TRANSFORM, body=pkl_dumps_lz4(input_data))
    put_object(key=WorkerKey.LOAD, body=pkl_dumps_lz4(initial_processed_data))

    # Execute the transform worker
    response = transform_bulk.handler(event={}, context=None)

    assert response == {
        "stage_name": "transform",
        "processed_records": 13,
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

    created_objects: list[dict[str, dict]] = pkl_loads_lz4(output_data)
    assert_transform_outputs_equal(created_objects, template_output)


@pytest.mark.parametrize("path_to_edge_case", (PATH_TO_HERE / "edge_cases").iterdir())
def test_transform_worker_edge_cases(
    path_to_edge_case: Path,
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
):

    from etl.sds.worker.bulk.transform_bulk import transform_bulk

    initial_processed_data = deque([])

    # Initial state
    with open(path_to_edge_case / "transform_bulk_input.json") as f:
        input_data = deque(json_load(f))
    put_object(key=WorkerKey.TRANSFORM, body=pkl_dumps_lz4(input_data))
    put_object(key=WorkerKey.LOAD, body=pkl_dumps_lz4(initial_processed_data))

    # Execute
    response = transform_bulk.handler(event={}, context=None)
    assert response["error_message"] is None

    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM)
    final_processed_data: str = get_object(key=WorkerKey.LOAD)
    n_final_processed = len(pkl_loads_lz4(final_processed_data))
    n_final_unprocessed = len(pkl_loads_lz4(final_unprocessed_data))

    assert n_final_unprocessed == response["unprocessed_records"]
    assert n_final_processed == response["processed_records"]
