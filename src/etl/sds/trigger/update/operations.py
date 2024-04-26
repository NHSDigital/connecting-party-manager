from pathlib import Path
from typing import TYPE_CHECKING

from etl_utils.constants import CHANGELOG_NUMBER  # , CHANGELOG_QUERY
from etl_utils.ldap_typing import LdapClientProtocol, LdapModuleProtocol
from etl_utils.ldif.model import DistinguishedName
from etl_utils.trigger.operations import object_exists
from nhs_context_logging import log_action
from sds.domain.changelog import ChangelogRecord

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class NoExistingChangeLogNumber(Exception):
    pass


class BadChangeLogNumber(Exception):
    pass


def get_certs_from_s3_truststore(
    s3_client: "S3Client", truststore_bucket: str, cert_file: Path, key_file: Path
):
    for key_path in (cert_file, key_file):
        s3_client.download_file(truststore_bucket, key_path.name, key_path)


def prepare_ldap_client(
    ldap: LdapModuleProtocol,
    ldap_host: str,
    cert_file: str,
    key_file: str,
    ldap_changelog_user: str,
    ldap_changelog_password: str,
) -> LdapClientProtocol:
    ldap_client = ldap.initialize(ldap_host)
    ldap_client.set_option(ldap.OPT_X_TLS_CERTFILE, cert_file)
    ldap_client.set_option(ldap.OPT_X_TLS_KEYFILE, key_file)
    ldap_client.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
    ldap_client.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
    ldap_client.simple_bind_s(ldap_changelog_user, ldap_changelog_password)
    return ldap_client


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


@log_action(log_args=["base", "scope", "filterstr", "attrlist"], log_result=True)
def _ldap_search(
    ldap_client: LdapClientProtocol,
    base: str,
    scope: str,
    filterstr: str,
    attrlist: list[str] = None,
):
    ldap_client.search(base=base, scope=scope, filterstr=filterstr, attrlist=attrlist)
    return ldap_client.result()


def get_latest_changelog_number_from_ldap(
    ldap_client: LdapClientProtocol, ldap: LdapModuleProtocol
) -> int:
    _, (record,) = _ldap_search(
        ldap_client=ldap_client,
        base="cn=Changelog,o=nhs",
        scope=ldap.SCOPE_BASE,
        filterstr="(objectClass=*)",
        attrlist=["firstchangenumber", "lastchangenumber"],
    )

    _, (unpack_record) = record

    return int(unpack_record["lastchangenumber"][0].decode("utf-8"))


def get_changelog_entries_from_ldap(
    ldap_client: LdapClientProtocol,
    ldap: LdapModuleProtocol,
    current_changelog_number: int,
    latest_changelog_number: int,
) -> list[tuple[str, dict]]:
    changelog_records = []
    for changelog_number in range(
        current_changelog_number + 1, latest_changelog_number + 1
    ):
        _, (record,) = _ldap_search(
            ldap_client=ldap_client,
            base="cn=Changelog,o=nhs",
            scope=ldap.SCOPE_ONELEVEL,
            filterstr=f"(changenumber={changelog_number})",
        )
        changelog_records.append(record)

    return changelog_records


def parse_changelog_changes(distinguished_name: str, record: dict) -> str:
    _distinguished_name = DistinguishedName.parse(distinguished_name)

    record_dict = {
        "object_class": record["objectClass"][0].decode("utf-8"),
        "change_number": record["changeNumber"][0].decode("utf-8"),
        "change_time": record["changeTime"][0].decode("utf-8"),
        "change_type": record["changeType"][0].decode("utf-8"),
        "target_distinguished_name": record["targetDN"][0].decode("utf-8"),
    }

    if "changes" in record:
        record_dict["changes"] = (
            record["changes"][0].decode("utf-8").replace("\\n", "\n")
        )  # I struggled to find a solution to this, so this is my hack

    changelog = ChangelogRecord(_distinguished_name=_distinguished_name, **record_dict)

    if changelog.change_type == "delete":
        return "\n".join(
            [
                f'dn: {record["targetDN"][0].decode("utf-8")}',
                f"changetype: {changelog.change_type}",
            ]
        )

    return "\n".join(
        [
            f'dn: {record["targetDN"][0].decode("utf-8")}',
            f"changetype: {changelog.change_type}",
            changelog.changes.strip("\n"),
        ]
    )
