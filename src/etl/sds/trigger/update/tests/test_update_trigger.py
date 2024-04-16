import os
from unittest import mock

import boto3
from etl_utils.constants import CHANGELOG_NUMBER
from moto import mock_aws

from etl.sds.trigger.update.steps import _start_execution

MOCKED_UPDATE_TRIGGER_ENVIRONMENT = {
    "AWS_DEFAULT_REGION": "us-east-1",
    "STATE_MACHINE_ARN": "state-machine",
    "NOTIFY_LAMBDA_ARN": "notify-lambda",
    "TRUSTSTORE_BUCKET": "truststore",
    "CPM_FQDN": "cpm-fqdn",
    "LDAP_HOST": "ldap-host",
    "ETL_BUCKET": "etl-bucket",
    "ETL_EXTRACT_INPUT_KEY": "etl-input",
}


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
