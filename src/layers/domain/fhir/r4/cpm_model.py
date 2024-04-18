import re
from typing import Literal
from uuid import UUID

from domain.core.device import DeviceKeyType, DeviceType
from domain.core.device_key import validate_key
from domain.core.validation import DEVICE_NAME_REGEX, ENTITY_NAME_REGEX, ODS_CODE_REGEX
from domain.ods import ODS_API_BASE
from pydantic import BaseModel as _BaseModel
from pydantic import Extra, Field, validator

SYSTEM = "connecting-party-manager"
DEVICE_KEY_TYPE_SYSTEM_RE = (
    rf"^{SYSTEM}/({'|'.join(DeviceKeyType._value2member_map_)})$"
)
PRODUCT_TEAM_ID_SYSTEM = f"{SYSTEM}/product-team-id"
DEVICE_TYPE_SYSTEM = f"{SYSTEM}/device-type"
DEVICE_TYPE_VALUE_RE = rf"^{'|'.join(DeviceType._value2member_map_)}$"


class BaseModel(_BaseModel, extra=Extra.forbid):
    pass


def ConstStrField(value):
    """Field that can only take the given value, and defaults to it"""
    return Field(default=value, regex=rf"^{value}$")


class ProductTeamIdentifier(BaseModel):
    system: str = ConstStrField(PRODUCT_TEAM_ID_SYSTEM)
    value: UUID

    def dict(self, *args, **kwargs):
        """Additionally converts UUID to string"""
        return {"system": self.system, "value": str(self.value)}


# class Link(BaseModel):
#     relation: str
#     url: str


class OdsIdentifier(BaseModel):
    system: str = ConstStrField(ODS_API_BASE)
    value: str = Field(regex=ODS_CODE_REGEX)


class OdsReference(BaseModel):
    identifier: OdsIdentifier


class DeviceName(BaseModel):
    name: str = Field(regex=DEVICE_NAME_REGEX)
    type: str = ConstStrField("user-friendly-name")


class DeviceDefinitionIdentifier(BaseModel):
    system: str = ConstStrField(DEVICE_TYPE_SYSTEM)
    value: str = Field(regex=DEVICE_TYPE_VALUE_RE)


class DeviceDefinitionReference(BaseModel):
    identifier: DeviceDefinitionIdentifier


class DeviceIdentifier(BaseModel):
    system: str = Field(regex=DEVICE_KEY_TYPE_SYSTEM_RE)
    value: str

    @property
    def key_type(self) -> DeviceKeyType:
        (_key_type,) = re.findall(DEVICE_KEY_TYPE_SYSTEM_RE, self.system)
        return DeviceKeyType(_key_type)

    def as_tuple(self) -> tuple[str, str]:
        return (self.system, self.value)


class DeviceOwnerReference(BaseModel):
    identifier: ProductTeamIdentifier


class Organization(BaseModel):
    resourceType: Literal["Organization"]
    identifier: list[ProductTeamIdentifier] = Field(min_items=1, max_items=1)
    name: str = Field(regex=ENTITY_NAME_REGEX)
    partOf: OdsReference


class Device(BaseModel):
    resourceType: Literal["Device"]
    deviceName: list[DeviceName] = Field(min_items=1, max_items=1)
    definition: DeviceDefinitionReference
    identifier: list[DeviceIdentifier] = Field(min_items=1)
    owner: DeviceOwnerReference

    @validator("identifier", each_item=True)
    def validate_key(identifier: DeviceIdentifier):
        if identifier and isinstance(identifier, DeviceIdentifier):
            validate_key(key=identifier.value, type=identifier.key_type)
        return identifier

    @validator("identifier")
    def no_duplicate_keys(identifier: list[DeviceIdentifier]):
        if identifier and isinstance(identifier, list):
            unique_identifiers = set(map(DeviceIdentifier.as_tuple, identifier))
            if len(unique_identifiers) != len(identifier):
                raise ValueError(
                    "It is forbidden to supply the same key multiple times"
                )

        return identifier

    @validator("identifier")
    def no_duplicate_product_keys(identifier: list[DeviceIdentifier]):
        if identifier and isinstance(identifier, list):
            count = sum(
                ident.system == "connecting-party-manager/product_id"
                for ident in identifier
            )
            if count > 1:
                raise ValueError("It is forbidden to supply a product_id")
        return identifier


class Bundle(BaseModel):
    resourceType: Literal["Bundle"]
    id: UUID
    total: str
    # link: [Link]


class CollectionBundle(Bundle):
    type: str = ConstStrField("collection")
    entry: list[Device]


class SearchsetBundle(Bundle):
    type: str = ConstStrField("searchset")
    entry: list[CollectionBundle]
