from typing import Literal
from uuid import UUID

from domain.core.validation import ENTITY_NAME_REGEX, ODS_CODE_REGEX
from domain.ods import ODS_API_BASE
from pydantic import BaseModel as _BaseModel
from pydantic import Extra, Field

SYSTEM = "connecting-party-manager"


class BaseModel(_BaseModel, extra=Extra.forbid):
    pass


def ConstStrField(value):
    """Field that can only take the given value, and defaults to it"""
    return Field(default=value, regex=rf"^{value}$")


class Identifier(BaseModel):
    system: str = ConstStrField(SYSTEM)
    value: UUID

    def dict(self, *args, **kwargs):
        """Additionally serializes UUID to string"""
        _dict = super().dict(*args, **kwargs)
        (_, _dict["value"]) = self.value.urn.split("urn:uuid:")
        return _dict


class OdsIdentifier(BaseModel):
    system: str = ConstStrField(ODS_API_BASE)
    value: str = Field(regex=ODS_CODE_REGEX)


class Reference(BaseModel):
    identifier: OdsIdentifier


class Organization(BaseModel):
    resourceType: Literal["Organization"]
    identifier: list[Identifier] = Field(min_items=1, max_items=1)
    name: str = Field(regex=ENTITY_NAME_REGEX)
    partOf: Reference
