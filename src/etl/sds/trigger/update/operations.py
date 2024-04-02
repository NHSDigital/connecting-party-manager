from io import StringIO
from typing import TYPE_CHECKING

from etl_utils.constants import CHANGELOG_NUMBER, CHANGELOG_QUERY
from etl_utils.ldif.ldif import parse_ldif
from etl_utils.trigger.operations import object_exists
from sds.domain.changelog import ChangelogRecord

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class NoExistingChangeLogNumber(Exception):
    pass


class BadChangeLogNumber(Exception):
    pass


def get_current_changelog_number_from_s3(s3_client: "S3Client", bucket: str) -> int:
    if not object_exists(s3_client=s3_client, bucket=bucket, key=CHANGELOG_NUMBER):
        raise NoExistingChangeLogNumber(
            f"No existing changelog number found in s3://{bucket}/{CHANGELOG_NUMBER}"
        )
    response = s3_client.get_object(Bucket=bucket, Key=CHANGELOG_NUMBER)
    changelog_number = response["Body"].read().decode()
    if not changelog_number.isdigit():
        raise BadChangeLogNumber(changelog_number)
    return int(changelog_number)


def get_latest_changelog_number_from_ldap(ldap_connection, scope):
    # ldap_connection.search(base="something", scope=scope)
    # return max(ldap_connection.result()["something?"])
    return "123"


def get_changelog_entries_from_ldap(
    ldap_connection, scope, current_changelog_number: int, latest_changelog_number: int
):
    ldif_collection = []
    for changelog_number in range(
        current_changelog_number + 1, latest_changelog_number + 1
    ):
        ldap_connection.search(
            base=CHANGELOG_QUERY.format(changelog_number), scope=scope
        )
        ldif_collection.append(ldap_connection.result())
    return ldif_collection


def parse_changelog_changes(ldif: str) -> str:
    ((distinguished_name, record),) = parse_ldif(
        file_opener=StringIO, path_or_data=ldif
    )
    return ChangelogRecord(_distinguished_name=distinguished_name, **record).changes
