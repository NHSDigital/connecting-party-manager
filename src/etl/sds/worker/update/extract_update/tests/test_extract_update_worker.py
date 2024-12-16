import json
import os
from collections import deque
from typing import Callable
from unittest import mock

import pytest
from etl_utils.constants import LDIF_RECORD_DELIMITER, WorkerKey
from etl_utils.io import EtlEncoder, pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from etl_utils.worker.model import WorkerEnvironment
from event.json import json_load, json_loads
from moto import mock_aws
from mypy_boto3_s3 import S3Client

from etl.sds.worker.update.tests.test_update_e2e import PATH_TO_STAGE_DATA

BUCKET_NAME = "my-bucket"


@pytest.fixture
def mock_s3_client():
    with mock_aws(), mock.patch.dict(
        os.environ,
        {"ETL_BUCKET": BUCKET_NAME, "AWS_DEFAULT_REGION": "us-east-1"},
        clear=True,
    ):
        from etl.sds.worker.update.extract_update import extract_update

        extract_update.ENVIRONMENT = WorkerEnvironment.build()
        extract_update.S3_CLIENT.create_bucket(Bucket=BUCKET_NAME)
        yield extract_update.S3_CLIENT


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


def _split_ldif(data: str) -> list[str]:
    return list(filter(bool, data.split(LDIF_RECORD_DELIMITER)))


def test_extract_worker_pass(
    put_object: Callable[[str], None], get_object: Callable[[str], bytes]
):
    from etl.sds.worker.update.extract_update import extract_update

    # Initial state
    with open(PATH_TO_STAGE_DATA / "0.extract_input.ldif") as f:
        input_data = f.read()

    put_object(key=WorkerKey.EXTRACT, body=input_data)
    put_object(key=WorkerKey.TRANSFORM, body=pkl_dumps_lz4(deque([])))

    # Execute the extract worker
    response = extract_update.handler(event={}, context=None)
    assert response == {
        "stage_name": "extract",
        "processed_records": 1,
        "unprocessed_records": 0,
        "error_message": None,
    }

    # Final state
    final_unprocessed_data: str = get_object(key=WorkerKey.EXTRACT).decode()
    output_data = get_object(key=WorkerKey.TRANSFORM)
    n_final_unprocessed = len(_split_ldif(final_unprocessed_data))

    with open(PATH_TO_STAGE_DATA / "1.extract_output.json") as f:
        expected_output_data = json_load(f)

    assert (
        json_loads(json.dumps(pkl_loads_lz4(output_data), cls=EtlEncoder))
        == expected_output_data
    )
    assert n_final_unprocessed == 0
