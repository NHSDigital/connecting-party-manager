from typing import ClassVar, Literal, Optional

from etl_utils.ldif.model import DistinguishedName
from pydantic import BaseModel, Field, validator
from sds.domain.base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from sds.domain.constants import ChangelogCommonName, ChangeType, OrganizationalUnitNhs


class InconsistentChangelogNumber(Exception):
    pass


class ChangelogDistinguishedName(BaseModel):
    change_number: str = Field(alias="changenumber")
    common_name: ChangelogCommonName = Field(alias="cn")
    organisation: OrganizationalUnitNhs = Field(alias="o")


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
        return changes

    def changes_as_ldif(self) -> str:
        change_lines = [
            f"dn: {self.target_distinguished_name.raw}",
            f"changetype: {self.change_type}",
        ]
        if self.change_type is not ChangeType.DELETE:
            change_lines.append(self.changes.strip("\n"))
        return "\n".join(change_lines)
