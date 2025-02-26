from typing import ClassVar, Literal

from pydantic import Field, validator
from sds.domain.base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from sds.domain.constants import ModificationType
from sds.domain.organizational_unit import OrganizationalUnitDistinguishedName


class ImmutableFieldError(ValueError):
    pass


IMMUTABLE_SDS_FIELDS = {
    "uniqueidentifier",
}


class SdsModificationRequest(SdsBaseModel):
    distinguished_name: OrganizationalUnitDistinguishedName = Field(exclude=True)
    OBJECT_CLASS: ClassVar[Literal["modify"]] = "modify"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)
    unique_identifier: str = Field(alias="uniqueidentifier")

    modifications: list[tuple[ModificationType, str, set[str]]]

    @validator("modifications")
    def validate_immutable_fields(
        cls, modifications: list[tuple[ModificationType, str, any]]
    ):
        for _, field, _ in modifications:
            if field in IMMUTABLE_SDS_FIELDS:
                raise ImmutableFieldError(field)
        return modifications
