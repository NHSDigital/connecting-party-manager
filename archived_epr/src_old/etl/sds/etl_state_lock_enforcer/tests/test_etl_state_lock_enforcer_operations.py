import os
from typing import TYPE_CHECKING
from unittest import mock

import boto3
import pytest
from etl.sds.etl_state_lock_enforcer.operations import etl_state_lock_doesnt_exist_in_s3
from etl_utils.constants import ETL_STATE_LOCK
from moto import mock_aws

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

BUCKET_NAME = "test-bucket"


@pytest.fixture
def s3_client():
    with mock_aws(), mock.patch.dict(
        os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}, clear=True
    ):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        yield s3_client


def test_etl_state_lock_doesnt_exist_in_s3_when_lock_exists(s3_client: "S3Client"):
    s3_client.put_object(Bucket=BUCKET_NAME, Key=ETL_STATE_LOCK, Body="state_lock")

    # Assert that the function returns False (indicating the lock exists)
    assert not etl_state_lock_doesnt_exist_in_s3(
        s3_client=s3_client, bucket=BUCKET_NAME
    )


def test_etl_state_lock_doesnt_exist_in_s3_when_lock_does_not_exist(
    s3_client: "S3Client",
):
    assert etl_state_lock_doesnt_exist_in_s3(s3_client=s3_client, bucket=BUCKET_NAME)
