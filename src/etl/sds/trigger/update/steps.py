import uuid
from itertools import starmap
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from etl_utils.constants import ETL_QUEUE_HISTORY, LDIF_RECORD_DELIMITER
from etl_utils.ldap_typing import LdapModuleProtocol
from etl_utils.trigger.model import StateMachineInput

from .operations import (
    get_certs_from_s3_truststore,
    get_changelog_entries_from_ldap,
    get_current_changelog_number_from_s3,
    get_latest_changelog_number_from_ldap,
    parse_changelog_changes,
    prepare_ldap_client,
)

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_sqs import SQSClient


class Cache(TypedDict):
    s3_client: "S3Client"
    sqs_client: "SQSClient"
    truststore_bucket: str
    ldap: LdapModuleProtocol
    ldap_host: str
    cert_file: Path
    key_file: Path
    etl_bucket: str
    etl_extract_input_key: str
    changenumber_batch: int


class CorruptChangelogNumber(Exception):
    pass


def _get_certs_from_s3_truststore(data, cache: Cache):
    return get_certs_from_s3_truststore(
        s3_client=cache["s3_client"],
        truststore_bucket=cache["truststore_bucket"],
        cert_file=cache["cert_file"],
        key_file=cache["key_file"],
    )


def _prepare_ldap_client(data, cache: Cache):
    return prepare_ldap_client(
        ldap=cache["ldap"],
        ldap_host=cache["ldap_host"],
        cert_file=str(cache["cert_file"]),
        key_file=str(cache["key_file"]),
        ldap_changelog_user=cache["ldap_changelog_user"],
        ldap_changelog_password=cache["ldap_changelog_password"],
    )


def _get_current_changelog_number_from_s3(data, cache: Cache):
    return get_current_changelog_number_from_s3(
        s3_client=cache["s3_client"], bucket=cache["etl_bucket"]
    )


def _get_latest_changelog_number_from_ldap(data, cache: Cache):
    ldap_client = data[_prepare_ldap_client]
    latest_changelog_number = get_latest_changelog_number_from_ldap(
        ldap_client=ldap_client, ldap=cache["ldap"]
    )
    current_changelog_number = data[_get_current_changelog_number_from_s3]
    if current_changelog_number > latest_changelog_number:
        raise CorruptChangelogNumber(
            "Somehow the current changelog number in "
            f"the SDS ETL {current_changelog_number} "
            f"is ahead of the latest changelog {latest_changelog_number} "
            "number available on SDS"
        )
    return latest_changelog_number  # needed?


def _get_changelog_entries_from_ldap(data, cache: Cache):
    current_changelog_number = data[_get_current_changelog_number_from_s3]
    latest_changelog_number = data[_get_latest_changelog_number_from_ldap]
    ldap_client = data[_prepare_ldap_client]
    changelog_records, latest_changelog_number = get_changelog_entries_from_ldap(
        ldap_client=ldap_client,
        ldap=cache["ldap"],
        current_changelog_number=current_changelog_number,
        latest_changelog_number=latest_changelog_number,
        changenumber_batch=cache["changenumber_batch"],
    )
    return changelog_records, latest_changelog_number


def _parse_and_join_changelog_changes(data, cache):
    changelog_records, _ = data[_get_changelog_entries_from_ldap]
    changes_ldif = starmap(parse_changelog_changes, changelog_records)
    return LDIF_RECORD_DELIMITER.join(changes_ldif)


def _create_state_machine_input(data, cache):
    current_changelog_number = data[_get_current_changelog_number_from_s3]
    _, latest_changelog_number = data[_get_changelog_entries_from_ldap]
    return StateMachineInput.update(
        changelog_number_start=current_changelog_number,
        changelog_number_end=latest_changelog_number,
    )  # needs to get changelog_number_end from elsewhere


def _put_changes_to_intermediate_history_file(data, cache: Cache):
    changes = data[_parse_and_join_changelog_changes]
    state_machine_input: StateMachineInput = data[_create_state_machine_input]

    return cache["s3_client"].put_object(
        Bucket=cache["etl_bucket"],
        Key=f"{ETL_QUEUE_HISTORY}/{state_machine_input.name}",
        Body=changes,
    )


def _publish_message_to_sqs_queue(data, cache: Cache):
    state_machine_input: StateMachineInput = data[_create_state_machine_input]
    message_body = state_machine_input.json_with_name()
    message_deduplication_id = str(uuid.uuid4())

    # Send the message to the SQS queue
    cache["sqs_client"].send_message(
        QueueUrl=cache["sqs_queue_url"],
        MessageBody=message_body,
        MessageGroupId="state_machine_group",
        MessageDeduplicationId=message_deduplication_id,
    )


steps = [
    _get_certs_from_s3_truststore,
    _prepare_ldap_client,
    _get_current_changelog_number_from_s3,
    _get_latest_changelog_number_from_ldap,
    _get_changelog_entries_from_ldap,
    _parse_and_join_changelog_changes,
    _create_state_machine_input,
    _put_changes_to_intermediate_history_file,
    _publish_message_to_sqs_queue,
]
