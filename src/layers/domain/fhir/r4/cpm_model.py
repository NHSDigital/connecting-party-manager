from typing import Literal
from uuid import UUID

from domain.core.validation import ENTITY_NAME_REGEX, ODS_CODE_REGEX
from pydantic import BaseModel as _BaseModel
from pydantic import Extra, Field


class BaseModel(_BaseModel, extra=Extra.forbid):
    pass


class Identifier(BaseModel):
    id: str = Field(regex=ODS_CODE_REGEX)
    value: str = Field(min_length=1)


class Reference(BaseModel):
    identifier: Identifier


class Organization(BaseModel):
    resourceType: Literal["Organization"]
    id: UUID
    name: str = Field(regex=ENTITY_NAME_REGEX)
    partOf: Reference

    def dict(self, *args, **kwargs):
        """Additionally serializes UUID to string"""
        _dict = super().dict(*args, **kwargs)
        (_, _dict["id"]) = self.id.urn.split("urn:uuid:")
        return _dict
