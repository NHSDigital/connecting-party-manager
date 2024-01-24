from typing import ClassVar, Literal, Optional

from pydantic import BaseModel, Field
from sds.domain.constants import OrganizationalUnitNhs, OrganizationalUnitServices

from .base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel  # , _lowercase_values


class OrganizationalUnitDistinguishedName(BaseModel):
    organisational_unit: OrganizationalUnitServices = Field(alias="ou")
    organisation: OrganizationalUnitNhs = Field(alias="o")
    unique_identifier: Optional[str] = Field(alias="uniqueidentifier", default=None)


class OrganizationalUnit(SdsBaseModel):
    distinguished_name: OrganizationalUnitDistinguishedName

    OBJECT_CLASS: ClassVar[Literal["organizationalunit"]] = "organizationalunit"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)
    organisational_unit: OrganizationalUnitServices = Field(alias="ou")
