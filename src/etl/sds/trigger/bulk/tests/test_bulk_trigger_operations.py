import os
from contextlib import nullcontext as does_not_raise
from typing import TYPE_CHECKING
from unittest import mock

import boto3
import pytest
from botocore.exceptions import ClientError
from etl_utils.constants import CHANGELOG_NUMBER
from moto import mock_aws

from etl.sds.trigger.bulk.operations import (
    ChangelogNumberExists,
    TableNotEmpty,
    validate_database_is_empty,
    validate_no_changelog_number,
)
from test_helpers.dynamodb import mock_table

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

BUCKET_NAME = "my-bucket"
TABLE_NAME = "my-table"


@pytest.fixture
def s3_client():
    with mock_aws(), mock.patch.dict(
        os.environ, {"AWS_DEFAULT_REGION": "us-east-1"}, clear=True
    ):
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        yield s3_client


@pytest.mark.parametrize(
    ["bucket", "changelog_number", "expectation"],
    [
        (BUCKET_NAME, None, does_not_raise()),
        (BUCKET_NAME, "123", pytest.raises(ChangelogNumberExists)),
        ("not-a-bucket", None, pytest.raises(ClientError)),
        ("not-a-bucket", "123", pytest.raises(ClientError)),
    ],
)
def test_validate_no_changelog_number(
    bucket, changelog_number, expectation, s3_client: "S3Client"
):
    if changelog_number is not None:
        s3_client.put_object(
            Bucket=BUCKET_NAME, Key=CHANGELOG_NUMBER, Body=changelog_number
        )

    with expectation:
        validate_no_changelog_number(s3_client=s3_client, source_bucket=bucket)


@pytest.mark.parametrize(
    ["item", "expectation"],
    [
        (None, does_not_raise()),
        ({"pk": {"S": "foo"}, "sk": {"S": "bar"}}, pytest.raises(TableNotEmpty)),
    ],
)
def test_validate_database_is_empty(item, expectation):
    with mock_table(table_name=TABLE_NAME) as client, expectation:
        if item is not None:
            client.put_item(TableName=TABLE_NAME, Item=item)
        validate_database_is_empty(dynamodb_client=client, table_name=TABLE_NAME)
