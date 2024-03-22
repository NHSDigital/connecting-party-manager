from typing import TYPE_CHECKING, TypedDict

from etl_utils.constants import LDIF_RECORD_DELIMITER
from etl_utils.trigger.model import StateMachineInput
from etl_utils.trigger.operations import start_execution, validate_state_keys_are_empty

from .operations import (
    get_changelog_entries_from_ldap,
    get_current_changelog_number_from_s3,
    get_latest_changelog_number_from_ldap,
    parse_changelog_changes,
)

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_stepfunctions import SFNClient


class Cache(TypedDict):
    s3_client: "S3Client"
    step_functions_client: "SFNClient"
    ldap_connection: None
    bucket: str
    key: str
    state_machine_arn: str


class CorruptChangelogNumber(Exception):
    pass


def _get_current_changelog_number_from_s3(data, cache: Cache):
    return get_current_changelog_number_from_s3(
        s3_client=cache["s3_client"], bucket=cache["bucket"]
    )


def _get_latest_changelog_number_from_ldap(data, cache: Cache):
    latest_changelog_number = get_latest_changelog_number_from_ldap(
        s3_client=cache["s3_client"], bucket=cache["bucket"]
    )
    current_changelog_number = data[_get_current_changelog_number_from_s3]
    if current_changelog_number > latest_changelog_number:
        raise CorruptChangelogNumber(
            "Somehow the current changelog number in "
            f"the SDS ETL {current_changelog_number} "
            f"is ahead of the latest changelog {latest_changelog_number} "
            "number available on SDS"
        )
    return latest_changelog_number


def _create_state_machine_input(data, cache):
    current_changelog_number = data[_get_current_changelog_number_from_s3]
    latest_changelog_number = data[_get_latest_changelog_number_from_ldap]
    return StateMachineInput.update(
        changelog_number_start=current_changelog_number,
        changelog_number_end=latest_changelog_number,
    )


def _validate_state_keys_are_empty(data, cache: Cache):
    return validate_state_keys_are_empty(
        s3_client=cache["s3_client"], bucket=cache["bucket"]
    )


def _get_changelog_entries_from_ldap(data, cache: Cache):
    current_changelog_number = data[_get_current_changelog_number_from_s3]
    latest_changelog_number = data[_get_latest_changelog_number_from_ldap]
    return get_changelog_entries_from_ldap(
        ldap_connection=cache["ldap_connection"],
        current_changelog_number=current_changelog_number,
        latest_changelog_number=latest_changelog_number,
    )


def _parse_changelog_changes(data, cache):
    ldif_collection: list[str] = data[_get_changelog_entries_from_ldap]
    return LDIF_RECORD_DELIMITER.join(map(parse_changelog_changes, ldif_collection))


def _put_to_state_machine(data, cache: Cache):
    changes = data[_parse_changelog_changes]
    return cache["s3_client"].put_object(
        Bucket=cache["bucket"], Key=cache["key"], Body=changes
    )


def _start_execution(data, cache):
    state_machine_input = data[_create_state_machine_input]
    return start_execution(
        step_functions_client=cache["step_functions_client"],
        state_machine_arn=cache["state_machine_arn"],
        state_machine_input=state_machine_input,
    )


def _put_to_history(data, cache: Cache):
    latest_changelog_number = data[_get_latest_changelog_number_from_ldap]
    changes = data[_parse_changelog_changes]
    return cache["s3_client"].put_object(
        Bucket=cache["bucket"],
        Key=f"history/changelog/{latest_changelog_number}/{cache['key']}",
        Body=changes,
    )


steps = [
    _get_current_changelog_number_from_s3,
    _get_latest_changelog_number_from_ldap,
    _create_state_machine_input,
    _validate_state_keys_are_empty,
    _get_changelog_entries_from_ldap,
    _parse_changelog_changes,
    _put_to_state_machine,
    _put_to_history,
    _start_execution,
]
