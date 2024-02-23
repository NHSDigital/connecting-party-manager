import json
import os
from contextlib import nullcontext as does_not_raise
from typing import TYPE_CHECKING
from unittest import mock

import boto3
import pytest
from botocore.exceptions import ClientError
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from etl_utils.trigger.model import StateMachineInput
from moto import mock_aws

from etl.sds.trigger.bulk.operations import (
    EMPTY_JSON_ARRAY,
    EMPTY_LDIF,
    ChangelogNumberExists,
    StateFileNotEmpty,
    TableNotEmpty,
    start_execution,
    validate_database_is_empty,
    validate_no_changelog_number,
    validate_state_keys_are_empty,
)
from test_helpers.dynamodb import mock_table

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

BUCKET_NAME = "my-bucket"
TABLE_NAME = "my-table"
STATE_MACHINE_DEFINITION = json.dumps(
    {
        "StartAt": "MyStep",
        "States": {"MyStep": {"Type": "Pass", "Result": {"foo": "bar"}, "End": True}},
    }
)


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
def test_validate_no_changelog_number(bucket, changelog_number, expectation, s3_client):
    if changelog_number is not None:
        s3_client.put_object(
            Bucket=BUCKET_NAME, Key=CHANGELOG_NUMBER, Body=changelog_number
        )

    with expectation:
        validate_no_changelog_number(s3_client=s3_client, source_bucket=bucket)


@pytest.mark.parametrize(
    "state_machine_input",
    (StateMachineInput.bulk(),),
)
def test_start_execution(state_machine_input: StateMachineInput):
    with mock_aws():
        step_functions_client = boto3.client("stepfunctions", region_name="us-east-1")
        iam_client = boto3.client("iam", region_name="us-east-1")
        iam_response = iam_client.create_role(
            RoleName="my-role", AssumeRolePolicyDocument="some policy"
        )
        create_response = step_functions_client.create_state_machine(
            name="my_state_machine",
            definition=STATE_MACHINE_DEFINITION,
            roleArn=iam_response["Role"]["Arn"],
        )
        execution_response = start_execution(
            step_functions_client=step_functions_client,
            state_machine_arn=create_response["stateMachineArn"],
            state_machine_input=state_machine_input,
        )
        execution_state = step_functions_client.describe_execution(
            executionArn=execution_response["executionArn"],
        )
    assert execution_state["status"] == "RUNNING"


@pytest.mark.parametrize(
    ["key", "expectation"],
    [
        (None, does_not_raise()),
        (WorkerKey.EXTRACT, pytest.raises(StateFileNotEmpty)),
        (WorkerKey.TRANSFORM, pytest.raises(StateFileNotEmpty)),
        (WorkerKey.LOAD, pytest.raises(StateFileNotEmpty)),
    ],
)
def test_validate_state_keys_are_empty(s3_client: "S3Client", key, expectation):
    s3_client.put_object(Bucket=BUCKET_NAME, Key=WorkerKey.EXTRACT, Body=EMPTY_LDIF)
    s3_client.put_object(
        Bucket=BUCKET_NAME, Key=WorkerKey.TRANSFORM, Body=EMPTY_JSON_ARRAY
    )
    s3_client.put_object(Bucket=BUCKET_NAME, Key=WorkerKey.LOAD, Body=EMPTY_JSON_ARRAY)

    if key is not None:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=b" ")
    with expectation:
        validate_state_keys_are_empty(s3_client=s3_client, source_bucket=BUCKET_NAME)


def test_validate_state_keys_are_empty_when_no_initial_state(s3_client: "S3Client"):
    with does_not_raise():
        validate_state_keys_are_empty(s3_client=s3_client, source_bucket=BUCKET_NAME)


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
