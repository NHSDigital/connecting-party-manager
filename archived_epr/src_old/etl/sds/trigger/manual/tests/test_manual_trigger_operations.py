import os
from contextlib import nullcontext as does_not_raise
from typing import TYPE_CHECKING
from unittest import mock

import boto3
import pytest
from etl.sds.trigger.manual.operations import (
    ExecutionHistoryEmpty,
    validate_bucket_contents,
)
from etl_utils.constants import ETL_STATE_MACHINE_HISTORY
from moto import mock_aws

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

BUCKET_NAME = "my-bucket"


@pytest.fixture
def s3_client():
    with mock_aws(), mock.patch.dict(
        os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}, clear=True
    ):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        yield s3_client


@pytest.mark.parametrize(
    ["bucket", "s3object", "expectation"],
    [
        (
            BUCKET_NAME,
            f"{ETL_STATE_MACHINE_HISTORY}/bulk.0.1234567.2024-07-03T14.04.12.721948",
            does_not_raise(),
        ),
        (BUCKET_NAME, None, pytest.raises(ExecutionHistoryEmpty)),
    ],
)
def test_execution_history(bucket, s3object, expectation, s3_client: "S3Client"):
    if s3object is not None:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3object, Body="foobar")

    with expectation:
        validate_bucket_contents(s3_client=s3_client, etl_bucket=bucket)
