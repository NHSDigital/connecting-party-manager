from typing import Literal

from pydantic import BaseModel as _BaseModel
from pydantic import EmailStr, Extra, Field


class BaseModel(_BaseModel, extra=Extra.forbid):
    pass


class HumanName(BaseModel):
    text: str


class ContactPoint(BaseModel):
    system: Literal["email"]
    value: EmailStr


class OrganizationContact(BaseModel):
    name: str
    telecom: list[ContactPoint] = Field(min_items=1, max_items=1)


class Identifier(BaseModel):
    id: str
    value: str


class Reference(BaseModel):
    identifier: Identifier


class Organization(BaseModel):
    resourceType: Literal["Organization"]
    id: str
    name: str
    partOf: Reference
    contact: list[OrganizationContact] = Field(min_items=1, max_items=1)
