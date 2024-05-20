from typing import ClassVar, Literal

from pydantic import Field
from sds.domain.base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from sds.domain.organizational_unit import OrganizationalUnitDistinguishedName


class SdsDeletionRequest(SdsBaseModel):
    distinguished_name: OrganizationalUnitDistinguishedName = Field(exclude=True)
    OBJECT_CLASS: ClassVar[Literal["delete"]] = "delete"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)
    unique_identifier: str = Field(alias="uniqueidentifier")
