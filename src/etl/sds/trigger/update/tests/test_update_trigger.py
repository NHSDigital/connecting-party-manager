import os
import time
from collections import deque
from functools import partial
from json import JSONDecodeError
from types import FunctionType
from unittest import mock

import boto3
import pytest
from botocore.exceptions import ClientError
from domain.core.device import DeviceType
from etl.clear_state_inputs import EMPTY_JSON_DATA, EMPTY_LDIF_DATA
from etl_utils.constants import CHANGELOG_NUMBER, WorkerKey
from etl_utils.io import pkl_dumps_lz4
from etl_utils.io.test.io_utils import pkl_loads_lz4
from event.aws.client import dynamodb_client
from event.json import json_loads
from moto import mock_aws
from mypy_boto3_s3 import S3Client

from etl.sds.trigger.update.steps import _start_execution
from etl.sds.worker.load.tests.test_load_worker import MockDeviceRepository
from test_helpers.dynamodb import clear_dynamodb_table
from test_helpers.terraform import read_terraform_output

MOCKED_UPDATE_TRIGGER_ENVIRONMENT = {
    "AWS_DEFAULT_REGION": "us-east-1",
    "STATE_MACHINE_ARN": "state-machine",
    "NOTIFY_LAMBDA_ARN": "notify-lambda",
    "TRUSTSTORE_BUCKET": "truststore",
    "CPM_FQDN": "cpm-fqdn",
    "LDAP_HOST": "ldap-host",
    "ETL_BUCKET": "etl-bucket",
    "ETL_EXTRACT_INPUT_KEY": "etl-input",
    "LDAP_CHANGELOG_USER": "user",
    "LDAP_CHANGELOG_PASSWORD": "eggs",  # pragma: allowlist secret
}

ALLOWED_EXCEPTIONS = (JSONDecodeError,)


def _ask_s3(s3_client: S3Client, bucket: str, key: str, question: FunctionType = None):
    result = True
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
    except ClientError:
        result = False

    if result and question is not None:
        data = response["Body"].read()
        try:
            result = question(data)
        except ALLOWED_EXCEPTIONS:
            result = False
    return result


CHANGELOG_NUMBER_VALUE = "538684"


def test_update():
    mocked_ldap = mock.Mock()
    mocked_ldap_client = mock.Mock()
    mocked_ldap.initialize.return_value = mocked_ldap_client
    mocked_ldap_client.result.return_value = (
        101,
        [
            (
                "changenumber=75852519,cn=changelog,o=nhs",
                {
                    "objectclass": {
                        "top",
                        "changeLogEntry",
                        "nhsExternalChangelogEntry",
                    },
                    "changenumber": "75852519",
                    "changes": "foo",
                    "changetime": "20240116173441Z",
                    "changetype": "add",
                    "targetdn": "uniqueIdentifier=200000042019,ou=Services,o=nhs",
                },
            ),
        ],
    )

    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_UPDATE_TRIGGER_ENVIRONMENT, clear=True
    ):
        s3_client = boto3.client("s3")

        # Create truststore contents
        s3_client.create_bucket(
            Bucket=MOCKED_UPDATE_TRIGGER_ENVIRONMENT["TRUSTSTORE_BUCKET"]
        )
        s3_client.put_object(
            Bucket=MOCKED_UPDATE_TRIGGER_ENVIRONMENT["TRUSTSTORE_BUCKET"],
            Key="cpm-fqdn.crt",
            Body="something",
        )
        s3_client.put_object(
            Bucket=MOCKED_UPDATE_TRIGGER_ENVIRONMENT["TRUSTSTORE_BUCKET"],
            Key="cpm-fqdn.key",
            Body="something",
        )

        # Create initial changelog number
        s3_client.create_bucket(Bucket=MOCKED_UPDATE_TRIGGER_ENVIRONMENT["ETL_BUCKET"])
        s3_client.put_object(
            Bucket=MOCKED_UPDATE_TRIGGER_ENVIRONMENT["ETL_BUCKET"],
            Key=CHANGELOG_NUMBER,
            Body="0",
        )

        from etl.sds.trigger.update import update

        # Mock the cache contents
        update.CACHE["s3_client"] = s3_client
        update.CACHE["ldap"] = mocked_ldap
        update.CACHE["ldap_client"] = mocked_ldap_client

        # Remove start execution, since it's meaningless
        idx = update.steps.index(_start_execution)
        update.steps.pop(idx)

        # Don't execute the notify lambda
        update.notify = mock.Mock(return_value="abc")

        response = update.handler()

    assert response == "abc"


@pytest.mark.timeout(30)
@pytest.mark.integration
def test_update_trigger_integration():
    # Where the state is located
    etl_bucket = read_terraform_output("sds_etl.value.bucket")
    table_name = read_terraform_output("dynamodb_table_name.value")

    client = dynamodb_client()
    repository = MockDeviceRepository(table_name=table_name, dynamodb_client=client)

    # Set some questions
    s3_client = boto3.client("s3")
    ask_s3 = partial(_ask_s3, s3_client=s3_client, bucket=etl_bucket)

    was_changelog_number_updated = lambda: ask_s3(
        key=CHANGELOG_NUMBER,
        question=lambda x: int(json_loads(x)) > int(CHANGELOG_NUMBER_VALUE),
    )

    was_state_machine_successful = (
        lambda: ask_s3(
            key=WorkerKey.EXTRACT,
            question=lambda x: x == b"",
        )
        and ask_s3(
            key=WorkerKey.TRANSFORM,
            question=lambda x: pkl_loads_lz4(x) == deque(),
        )
        and ask_s3(
            key=WorkerKey.LOAD,
            question=lambda x: pkl_loads_lz4(x) == deque(),
        )
        and repository.count(by=DeviceType.PRODUCT) > 0
    )

    # Clear/set the initial state
    s3_client.put_object(Bucket=etl_bucket, Key=WorkerKey.EXTRACT, Body=EMPTY_LDIF_DATA)
    s3_client.put_object(
        Bucket=etl_bucket, Key=WorkerKey.TRANSFORM, Body=pkl_dumps_lz4(EMPTY_JSON_DATA)
    )
    s3_client.put_object(
        Bucket=etl_bucket, Key=WorkerKey.LOAD, Body=pkl_dumps_lz4(EMPTY_JSON_DATA)
    )
    s3_client.put_object(
        Bucket=etl_bucket, Key=CHANGELOG_NUMBER, Body=CHANGELOG_NUMBER_VALUE
    )
    clear_dynamodb_table(client=client, table_name=table_name)

    # Trigger the bulk load
    event_client = boto3.client("events")
    rule_name = "Integration-test-update-lambda-rule"
    detail_type = "test-update-event"

    rule_arn = event_client.put_rule(
        Name=rule_name,
        EventPattern='{"source": ["aws.events"], "detail-type": ["'
        + detail_type
        + '"]}',
        State="ENABLED",
    )
    event_client.put_targets(
        Rule=rule_name,
        Targets=[
            {
                "Id": "1",
                "Arn": read_terraform_output("sds_etl.value.update_lambda_arn"),
            }
        ],
    )

    event_client.put_events(
        Entries=[
            {
                "Source": "Integration-test-event",
                "DetailType": detail_type,
                "Detail": "{}",
                "EventBusName": "default",
                "Resources": [rule_arn["RuleArn"]],
            }
        ]
    )

    changelog_number_updated = False
    state_machine_successful = False
    while not all(
        (
            changelog_number_updated,
            state_machine_successful,
        )
    ):
        time.sleep(5)
        changelog_number_updated = (
            changelog_number_updated or was_changelog_number_updated()
        )
        state_machine_successful = (
            state_machine_successful or was_state_machine_successful()
        )

    # Confirm the final state
    assert changelog_number_updated
    assert state_machine_successful

    deleteme = event_client.delete_rule(Name=rule_name)
