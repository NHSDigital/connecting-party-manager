import os
import re
from collections import deque
from itertools import permutations
from math import ceil
from typing import Callable
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from etl_utils.constants import WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from etl_utils.smart_open import smart_open
from moto import mock_aws
from mypy_boto3_s3 import S3Client

from etl.sds.worker.transform_bulk.utils import smart_open_if_exists

BUCKET_NAME = "my-bucket"
TABLE_NAME = "my-table"

GOOD_SDS_RECORD_AS_JSON = {
    "description": None,
    "distinguished_name": {
        "organisation": "nhs",
        "organisational_unit": "services",
        "unique_identifier": None,
    },
    "nhs_approver_urp": "uniqueIdentifier=562983788547,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs",
    "nhs_as_acf": None,
    "nhs_as_category_bag": None,
    "nhs_as_client": ["RVL"],
    "nhs_as_svc_ia": ["urn:nhs:names:services:pds:QUPA_IN040000UK01"],
    "nhs_date_approved": "20090601140104",
    "nhs_date_requested": "20090601135904",
    "nhs_id_code": "RVL",
    "nhs_mhs_manufacturer_org": "LSP04",
    "nhs_mhs_party_key": "RVL-806539",
    "nhs_product_key": "634",
    "nhs_product_name": "Cerner Millennium",
    "nhs_product_version": "2005.02",
    "nhs_requestor_urp": "uniqueIdentifier=977624345541,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs",
    "nhs_temp_uid": "9713",
    "object_class": "nhsAS",
    "unique_identifier": "000428682512",
}

BAD_SDS_RECORD_AS_JSON = {}

FATAL_SDS_RECORD_AS_JSON = "<not_json"


PROCESSED_SDS_JSON_RECORD = {}  # dummy value, doesn't matter for transform


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
        from etl.sds.worker.transform_bulk import transform_bulk

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


def test_transform_worker_pass_no_dupes(
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
):
    from etl.sds.worker.transform_bulk import transform_bulk

    initial_unprocessed_data = deque([GOOD_SDS_RECORD_AS_JSON])
    initial_processed_data = deque([])

    # Initial state
    n_initial_unprocessed = len(initial_unprocessed_data)
    n_initial_processed = len(initial_processed_data)
    put_object(key=WorkerKey.TRANSFORM, body=pkl_dumps_lz4(initial_unprocessed_data))
    put_object(key=WorkerKey.LOAD, body=pkl_dumps_lz4(initial_processed_data))

    # Execute the transform worker
    response = transform_bulk.handler(event={}, context=None)

    assert response == [
        {
            "stage_name": "transform",
            "processed_records": n_initial_processed + n_initial_unprocessed,
            "unprocessed_records": 0,
            "s3_input_path": "s3://my-bucket/input--load/unprocessed.0",
            "error_message": None,
        }
    ]

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM)
    final_processed_data: str = get_object(key=f"{WorkerKey.LOAD}.0")
    n_final_unprocessed = len(pkl_loads_lz4(final_unprocessed_data))
    n_final_processed = len(pkl_loads_lz4(final_processed_data))

    # Confirm that everything has now been processed, and that there is no
    # unprocessed data left in the bucket
    assert n_final_processed == n_initial_processed + n_initial_unprocessed
    assert n_final_unprocessed == 0


@pytest.mark.parametrize("max_records", range(1, 10))
def test_transform_worker_pass_no_dupes_max_records(
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
    max_records: int,
):
    from etl.sds.worker.transform_bulk import transform_bulk

    initial_unprocessed_data = deque([GOOD_SDS_RECORD_AS_JSON] * 10)
    initial_processed_data = deque([])

    # Initial state
    n_initial_unprocessed = len(initial_unprocessed_data)
    n_initial_processed = len(initial_processed_data)
    put_object(key=WorkerKey.TRANSFORM, body=pkl_dumps_lz4(initial_unprocessed_data))
    put_object(key=WorkerKey.LOAD, body=pkl_dumps_lz4(initial_processed_data))

    expected_responses = []
    expected_iterations = min(
        ceil(n_initial_unprocessed / max_records), transform_bulk.FAN_OUT
    )

    total_processed = 0
    for i in range(expected_iterations):
        chunk_size = min(n_initial_unprocessed - total_processed, max_records)

        total_processed += chunk_size
        expected_responses.append(
            {
                "stage_name": "transform",
                "processed_records": chunk_size,
                "unprocessed_records": (n_initial_unprocessed - total_processed),
                "s3_input_path": f"s3://my-bucket/input--load/unprocessed.{i}",
                "error_message": None,
            }
        )

    # Execute the transform worker
    responses = transform_bulk.handler(event={"max_records": max_records}, context=None)

    assert responses == expected_responses

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM)
    n_final_unprocessed = len(pkl_loads_lz4(final_unprocessed_data))

    n_final_processed = 0
    for i in range(expected_iterations):
        final_processed_data: str = get_object(key=f"{WorkerKey.LOAD}.{i}")
        n_final_processed += len(pkl_loads_lz4(final_processed_data))

    # Confirm that everything has now been processed, and that there is no
    # unprocessed data left in the bucket
    assert n_final_processed == n_initial_processed + n_initial_unprocessed
    assert n_final_unprocessed == n_initial_unprocessed - total_processed


@pytest.mark.parametrize(
    "initial_unprocessed_data",
    permutations(
        [BAD_SDS_RECORD_AS_JSON, GOOD_SDS_RECORD_AS_JSON, GOOD_SDS_RECORD_AS_JSON]
    ),
)
def test_transform_worker_bad_record(
    initial_unprocessed_data: str,
    put_object: Callable[[str], None],
    get_object: Callable[[str], bytes],
):
    from etl.sds.worker.transform_bulk import transform_bulk

    _initial_unprocessed_data = pkl_dumps_lz4(deque(initial_unprocessed_data))
    bad_record_index = initial_unprocessed_data.index(BAD_SDS_RECORD_AS_JSON)

    # Initial state
    n_initial_unprocessed = len(initial_unprocessed_data)
    put_object(key=WorkerKey.TRANSFORM, body=_initial_unprocessed_data)

    # Execute the transform worker
    responses = transform_bulk.handler(event={}, context=None)
    assert len(responses) == 1

    responses[0]["error_message"] = responses[0]["error_message"].split("\n")[:6]

    assert responses[0] == {
        "stage_name": "transform",
        "processed_records": bad_record_index,
        "unprocessed_records": n_initial_unprocessed - bad_record_index,
        "s3_input_path": "s3://my-bucket/input--load/unprocessed.0",
        "error_message": [
            "The following errors were encountered",
            "  -- Error 1 (KeyError) --",
            f"  Failed to parse record {bad_record_index}",
            "  {}",
            "  'object_class'",
            "Traceback (most recent call last):",
        ],
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM)
    final_processed_data: str = get_object(key=f"{WorkerKey.LOAD}.0")
    n_final_unprocessed = len(pkl_loads_lz4(final_unprocessed_data))
    n_final_processed = len(pkl_loads_lz4(final_processed_data))

    # Confirm that there are still unprocessed records, and that there may have been
    # some records processed successfully
    assert n_final_unprocessed > 0
    assert n_final_processed == bad_record_index
    assert n_final_unprocessed == n_initial_unprocessed - bad_record_index


def test_transform_worker_fatal_record(
    put_object: Callable[[str], None], get_object: Callable[[str], str]
):
    from etl.sds.worker.transform_bulk import transform_bulk

    # Initial state
    initial_unprocessed_data = FATAL_SDS_RECORD_AS_JSON
    put_object(key=WorkerKey.TRANSFORM, body=initial_unprocessed_data)

    # Execute the transform worker
    responses = transform_bulk.handler(event={}, context=None)
    assert len(responses) == 1

    # The line number in the error changes for each example, so
    # substitute it for the value 'NUMBER'
    responses[0]["error_message"] = re.sub(
        r"Line \d{1,2}", "Line NUMBER", responses[0]["error_message"]
    )
    responses[0]["error_message"] = responses[0]["error_message"].split("\n")[:3]

    assert responses[0] == {
        "stage_name": "transform",
        "processed_records": None,
        "unprocessed_records": None,
        "s3_input_path": "s3://my-bucket/input--load/unprocessed.0",
        "error_message": [
            "The following errors were encountered",
            "  -- Error 1 (RuntimeError) --",
            "  LZ4F_decompress failed with code: ERROR_frameType_unknown",
        ],
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.TRANSFORM).decode()

    with pytest.raises(ClientError):
        get_object(key=f"{WorkerKey.LOAD}.0")

    # Confirm that no changes were persisted
    assert final_unprocessed_data == initial_unprocessed_data


def test_smart_open_if_exists(mock_s3_client: "S3Client"):
    s3_path = f"s3://{BUCKET_NAME}/some_file"
    initial_content = b"hiya"
    final_content = b"bye"

    # Set initial content via a default value
    with smart_open_if_exists(
        s3_client=mock_s3_client, s3_path=s3_path, empty_content=initial_content
    ) as f:
        assert f.read() == initial_content

    # Overwrite with standard smart_open
    with smart_open(s3_client=mock_s3_client, s3_path=s3_path, mode="wb") as f:
        f.write(final_content)

    # Verify not overwritten with default value
    with smart_open_if_exists(
        s3_client=mock_s3_client, s3_path=s3_path, empty_content=initial_content
    ) as f:
        assert f.read() == final_content
