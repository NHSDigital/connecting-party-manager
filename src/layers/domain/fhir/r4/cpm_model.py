from typing import Literal

from pydantic import BaseModel as _BaseModel
from pydantic import EmailStr, Extra, Field


class BaseModel(_BaseModel, extra=Extra.forbid):
    pass


class HumanName(BaseModel):
    text: str = Field(min_length=1)


class ContactPoint(BaseModel):
    system: Literal["email"]
    value: EmailStr


class OrganizationContact(BaseModel):
    name: HumanName
    telecom: list[ContactPoint] = Field(min_items=1, max_items=1)


class Identifier(BaseModel):
    id: str = Field(min_length=1)
    value: str = Field(min_length=1)


class Reference(BaseModel):
    identifier: Identifier


class Organization(BaseModel):
    resourceType: Literal["Organization"]
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    partOf: Reference
