import json
import os
from json import JSONDecodeError
from unittest import mock

import boto3
import pytest
from etl_utils.constants import CHANGELOG_NUMBER
from moto import mock_aws

MOCKED_UPDATE_TRIGGER_ENVIRONMENT = {
    "AWS_DEFAULT_REGION": "us-east-1",
    "STATE_MACHINE_ARN": "state-machine",
    "NOTIFY_LAMBDA_ARN": "notify-lambda",
    "TRUSTSTORE_BUCKET": "truststore",
    "CPM_FQDN": "cpm-fqdn",
    "LDAP_HOST": "ldap-host",
    "ETL_BUCKET": "etl-bucket",
    "LDAP_CHANGELOG_USER": "user",
    "LDAP_CHANGELOG_PASSWORD": "eggs",  # pragma: allowlist secret
    "SQS_QUEUE_URL": "sqs-queue.fifo",
}

ALLOWED_EXCEPTIONS = (JSONDecodeError,)
LATEST_CHANGELOG_NUMBER = b"540382"
CURRENT_CHANGELOG_NUMBER = str(int(LATEST_CHANGELOG_NUMBER) - 1).encode()

CHANGELOG_NUMBER_RESULT = [
    101,
    [
        [
            "cn=changelog,o=nhs",
            {
                "firstchangenumber": [b"46425"],
                "lastchangenumber": [LATEST_CHANGELOG_NUMBER],
            },
        ]
    ],
]

CHANGE_RESULT = (
    101,
    [
        [
            "changenumber=540246,cn=changelog,o=nhs",
            {
                "objectClass": [
                    b"top",
                    b"changeLogEntry",
                    b"nhsExternalChangelogEntry",
                ],
                "changeNumber": [b"540246"],
                "changes": [
                    b"\\nobjectClass: nhsmhsservice\\nobjectClass: top\\nnhsIDCode: F2R5Q\\nnhsMHSPartyKey: F2R5Q-823886\\nnhsMHSServiceName: urn:nhs:names:services:pdsquery\\nuniqueIdentifier: 4d554a907e83a4067695"
                ],
                "changeTime": [b"20240502100040Z"],
                "changeType": [b"add"],
                "targetDN": [
                    b"uniqueIdentifier=4d554a907e83a4067695,ou=Services,o=nhs"
                ],
            },
        ]
    ],
)

CHANGE_RESULT_WITHOUT_UNIQUE_IDENTIFIER = (
    101,
    [
        [
            "changenumber=540246,cn=changelog,o=nhs",
            {
                "objectClass": [
                    b"top",
                    b"changeLogEntry",
                    b"nhsExternalChangelogEntry",
                ],
                "changeNumber": [b"540246"],
                "changes": [
                    b"\\nobjectClass: nhsmhsservice\\nobjectClass: top\\nnhsIDCode: F2R5Q\\nnhsMHSPartyKey: F2R5Q-823886\\nnhsMHSServiceName: urn:nhs:names:services:pdsquery\\n"
                ],
                "changeTime": [b"20240502100040Z"],
                "changeType": [b"add"],
                "targetDN": [
                    b"uniqueIdentifier=4d554a907e83a4067695,ou=Services,o=nhs"
                ],
            },
        ]
    ],
)


CHANGE_AS_LDIF = """dn: o=nhs,ou=services,uniqueidentifier=4d554a907e83a4067695
changetype: add
objectClass: nhsmhsservice
objectClass: top
nhsIDCode: F2R5Q
nhsMHSPartyKey: F2R5Q-823886
nhsMHSServiceName: urn:nhs:names:services:pdsquery
uniqueIdentifier: 4d554a907e83a4067695""".encode()


@pytest.mark.parametrize(
    "change_result", [CHANGE_RESULT, CHANGE_RESULT_WITHOUT_UNIQUE_IDENTIFIER]
)
def test_update(change_result):
    mocked_ldap = mock.Mock()
    mocked_ldap_client = mock.Mock()
    mocked_ldap.initialize.return_value = mocked_ldap_client
    mocked_ldap_client.result.side_effect = (CHANGELOG_NUMBER_RESULT, change_result)

    with mock_aws(), mock.patch.dict(
        os.environ, MOCKED_UPDATE_TRIGGER_ENVIRONMENT, clear=True
    ), mock.patch("etl_utils.trigger.model.datetime") as mocked_datetime:
        mocked_datetime.datetime.now().isoformat.return_value = "foo"
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
            Body=CURRENT_CHANGELOG_NUMBER,
        )

        # mock sqs queue
        sqs = boto3.resource("sqs")
        queue = sqs.create_queue(
            QueueName=MOCKED_UPDATE_TRIGGER_ENVIRONMENT["SQS_QUEUE_URL"],
            Attributes={"FifoQueue": "true"},
        )

        from etl.sds.trigger.update import update

        # Mock the cache contents
        update.CACHE["s3_client"] = s3_client
        update.CACHE["sqs_queue_url"] = queue.url
        update.CACHE["ldap"] = mocked_ldap
        update.CACHE["ldap_client"] = mocked_ldap_client

        # Don't execute the notify lambda
        update.notify = (
            lambda lambda_client, function_name, result, trigger_type: result
        )

        # Execute the test
        response = update.handler()

        # Verify the changelog number is NOT updated (as it should be updated in the ETL, not the trigger)
        changelog_number_response = s3_client.get_object(
            Bucket=MOCKED_UPDATE_TRIGGER_ENVIRONMENT["ETL_BUCKET"], Key=CHANGELOG_NUMBER
        )
        assert changelog_number_response["Body"].read() == CURRENT_CHANGELOG_NUMBER

        decoded_current_changelog_number = int(CURRENT_CHANGELOG_NUMBER.decode())
        decoded_latest_changelog_number = int(LATEST_CHANGELOG_NUMBER.decode())

        # Verify the history file was created
        etl_history_response = s3_client.get_object(
            Bucket=MOCKED_UPDATE_TRIGGER_ENVIRONMENT["ETL_BUCKET"],
            Key=f"history/update.EXTRACT.{decoded_current_changelog_number}.{decoded_latest_changelog_number}.foo",
        )
        assert etl_history_response["Body"].read().lower() == CHANGE_AS_LDIF.lower()

        # Verify message was published to queue
        expected_sqs_message = json.dumps(
            {
                "init": "input--extract/unprocessed",
                "changelog_number_start": decoded_current_changelog_number,
                "changelog_number_end": decoded_latest_changelog_number,
                "type": "update",
                "timestamp": "foo",
                "name": f"update.EXTRACT.{decoded_current_changelog_number}.{decoded_latest_changelog_number}.foo",
            }
        )
        sqs_messages = queue.receive_messages()
        assert (
            sqs_messages[0].body == expected_sqs_message
        ), "SQS message does not match expected"

    assert not isinstance(response, Exception), response
