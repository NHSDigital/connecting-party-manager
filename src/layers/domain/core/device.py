from dataclasses import dataclass
from enum import StrEnum, auto
from uuid import UUID, uuid4

from pydantic import Field

from .aggregate_root import AggregateRoot
from .device_key import DeviceKey, DeviceKeyType
from .error import DuplicateError
from .event import Event
from .validation import DEVICE_NAME_REGEX


@dataclass(kw_only=True, slots=True)
class DeviceCreatedEvent(Event):
    id: str
    name: str
    type: "DeviceType"
    product_team_id: UUID
    ods_code: str
    status: "DeviceStatus"


@dataclass(kw_only=True, slots=True)
class DeviceKeyAddedEvent(Event):
    id: str
    key: str
    type: DeviceKeyType


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
    # SERVICE = auto()
    # API = auto()


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

    id: UUID = Field(default_factory=uuid4)
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
