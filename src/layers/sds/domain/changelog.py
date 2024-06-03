from typing import ClassVar, Literal, Optional

from etl_utils.ldif.model import DistinguishedName
from pydantic import BaseModel, Field, validator
from sds.domain.base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from sds.domain.constants import (
    REPLACE_UNIQUE_IDENTIFIER,
    ChangelogCommonName,
    ChangeType,
    OrganizationalUnitNhs,
)


class InconsistentChangelogNumber(Exception):
    pass


class ChangelogDistinguishedName(BaseModel):
    change_number: str = Field(alias="changenumber")
    common_name: ChangelogCommonName = Field(alias="cn")
    organisation: OrganizationalUnitNhs = Field(alias="o")


def _is_replacing_unique_identifier(ldif_lines: list[str]):
    return any(REPLACE_UNIQUE_IDENTIFIER in ldif for ldif in ldif_lines)


def _contains_unique_identifier_line(
    ldif_lines: list[str], unique_identifier_line: str
):
    """
    If this LDIF is replacing the unique identifier, we expect the
    'unique_identifier_line' to appear multiple times, once per replace
    statement, and once to indicate what is being replaced.

    Otherwise, it should appear once to indicate what is being
    added/deleted/modified.

    In practice we allow for bad LDIF where the same unique identifier
    appears multiple times, since our handling of LDIF explicitly
    deduplicates anyway - and so our conditions are ">" rather than "=="
    """
    n_unique_identifier_lines = ldif_lines.count(unique_identifier_line)
    if _is_replacing_unique_identifier(ldif_lines=ldif_lines):
        return n_unique_identifier_lines > 1
    return n_unique_identifier_lines > 0


class ChangelogRecord(SdsBaseModel):
    distinguished_name: ChangelogDistinguishedName

    OBJECT_CLASS: ClassVar[Literal["changelogentry"]] = "changelogentry"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)

    change_number: str = Field(alias="changenumber")
    changes: Optional[str] = ""
    change_time: str = Field(alias="changetime")
    change_type: ChangeType = Field(alias="changetype")
    target_distinguished_name: DistinguishedName = Field(alias="targetdn")

    @validator("target_distinguished_name", pre=True)
    def parse_target_distinguished_name(cls, target_distinguished_name):
        return DistinguishedName.parse(target_distinguished_name)

    @validator("change_number")
    def validate_change_number(
        cls, change_number, values: dict[str, ChangelogDistinguishedName]
    ):
        dn = values.get("distinguished_name")
        if dn is None:
            return change_number
        if change_number != dn.change_number:
            raise InconsistentChangelogNumber(
                f"change number '{change_number}' is not consistent "
                f"with DN change number '{dn.change_number}'"
            )
        return change_number

    @validator("changes")
    def validate_changes(cls, changes):
        if isinstance(changes, bytes):
            changes = changes.decode("unicode_escape")
        return changes.strip("\n")

    def changes_as_ldif(self) -> str:
        distinguished_name = dict(self.target_distinguished_name.parts)
        unique_identifier_line = (
            f"uniqueidentifier: {distinguished_name['uniqueidentifier']}"
        )
        header_lines = [
            f"dn: {self.target_distinguished_name.raw}",
            f"changetype: {self.change_type}",
        ]
        change_lines = header_lines + list(filter(bool, self.changes.split("\n")))

        if self.change_type is not ChangeType.ADD:
            change_lines.append(f"{OBJECT_CLASS_FIELD_NAME}: {self.change_type}")

        _lower_lines = list(map(str.lower, change_lines))
        if not _contains_unique_identifier_line(
            ldif_lines=_lower_lines, unique_identifier_line=unique_identifier_line
        ):
            change_lines.append(unique_identifier_line)

        return "\n".join(change_lines)
