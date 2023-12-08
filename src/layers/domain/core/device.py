import re
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import TypedDict
from uuid import UUID

from pydantic import BaseModel, Field, validator

from .aggregate_root import AggregateRoot
from .error import DuplicateError
from .event import Event
from .product_id import PRODUCT_ID_REGEX
from .validation import ACCREDITED_SYSTEM_ID_REGEX, DEVICE_NAME_REGEX


@dataclass(kw_only=True, slots=True)
class DeviceCreatedEvent(Event):
    id: UUID
    name: str
    type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    status: "DeviceStatus"


@dataclass(kw_only=True, slots=True)
class DeviceKeyAddedEvent(Event):
    id: UUID
    key: str
    type: "DeviceKeyType"


class DeviceKeyType(StrEnum):
    PRODUCT_ID = auto()
    ACCREDITED_SYSTEM_ID = auto()
    # SERVICE_NOW_ID = auto()

    @property
    def pattern(self) -> re.Pattern:
        match self:
            case DeviceKeyType.PRODUCT_ID:
                return PRODUCT_ID_REGEX
            case DeviceKeyType.ACCREDITED_SYSTEM_ID:
                return ACCREDITED_SYSTEM_ID_REGEX
            case _:
                raise NotImplementedError(f"No ID validation configured for '{self}'")


class DeviceKey(BaseModel):
    """
    A Device Key is a secondary way of indexing / retrieving Devices
    """

    type: DeviceKeyType
    key: str

    @validator("key", check_fields=True)
    def validate_key(key: str, values: dict):
        type: DeviceKeyType = values.get("type")
        if type and type.pattern.match(key) is None:
            raise ValueError(
                f"Key '{key}' does not match the expected "
                f"pattern '{type.pattern.pattern}' associated with "
                f"key type '{type}'"
            )
        return key


class DeviceKeyDict(TypedDict):
    type: str
    key: str


class DeviceType(StrEnum):
    """
    A Product is to be classified as being one of the following.  These terms
    were provided by Aubyn Crawford in collaboration with Service Now.

    NOTE:
        A 'SERVICE' and 'API' is NOT what a developer would expect them to be.
        These are terms from the problem domain and relate to how Assurance
        is performed.
    """

    PRODUCT = auto()
    SERVICE = auto()
    API = auto()


class DeviceStatus(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()  # "soft" delete


class Device(AggregateRoot):
    """
    An entity in the database.  It could model all sorts of different logical or
    physical entities:
    e.g.
        NRL (SERVICE)
        +-- NRL.v2 (API)
        |   +-- nrl (???)
        +-- NRL.v3 (API)
            +-- nrl-consumer-api (???)
            +-- nrl-producer-api (???)
    """

    id: UUID
    name: str = Field(regex=DEVICE_NAME_REGEX)
    type: DeviceType
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE)
    product_team_id: UUID
    ods_code: str
    keys: dict[str, DeviceKey] = Field(default_factory=dict, exclude=True)

    def rename(self, name: str):
        """
        Demonstrating that `renaming` is a specific operation and not just a
        CRUD update.
        """
        raise NotImplementedError()

    def add_key(self, type: str, key: str) -> DeviceKeyAddedEvent:
        """
        Adds a new Key to a Device
        """
        if key in self.keys:
            raise DuplicateError(f"It is forbidden to supply duplicate keys: '{key}'")
        device_key = DeviceKey(key=key, type=type)
        event = DeviceKeyAddedEvent(id=self.id, **device_key.dict())
        self.keys[key] = device_key
        return self.add_event(event=event)
