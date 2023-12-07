from dataclasses import dataclass
from enum import StrEnum, auto
from uuid import UUID

from domain.core.accredited_system_id import AccreditedSystemId
from domain.core.aggregate_root import AggregateRoot
from domain.core.error import DuplicateError, InvalidDeviceKeyError
from domain.core.event import Event
from domain.core.product_id import ProductId
from pydantic import BaseModel, Field


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
    key: ProductId | AccreditedSystemId
    type: "DeviceKeyType"


class DeviceKeyType(StrEnum):
    PRODUCT_ID = auto()
    # XXX-XXX-XXX
    ACCREDITED_SYSTEM_ID = auto()
    # \d{1,12}
    SERVICE_NOW_ID = auto()
    # TBD


class DeviceKey(BaseModel):
    """
    A Device Key is a secondary way of indexing / retrieving Devices.  These are expected to be:
      Product Id                    - e.g. XXX-XXX-XXX
      Accredited System Id (ASID)   - e.g. 123456789012
      Service Now Id                - e.g. TBD
    """

    type: DeviceKeyType


class DeviceType(StrEnum):
    """
    A Device is to be classified as being one of the following.  These terms
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
    name: str = Field(pattern="^[a-z][a-z0-9_]+$")
    type: DeviceType
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE)
    product_team_id: UUID
    ods_code: str
    keys: dict[str, DeviceKey] = Field(default_factory=dict, exclude=True)
    # relationships: dict[UUID, Relationship] = Field(default_factory=dict, exclude=True)
    # pages: dict[str, DevicePage] = Field(default_factory=dict, exclude=True)

    def rename(self, name: str):
        """
        Demonstrating that `renaming` is a specific operation and not just a
        CRUD update.
        """
        raise NotImplementedError()

    def add_key(self, key: ProductId | AccreditedSystemId) -> DeviceKeyAddedEvent:
        """
        Adds a new Key to a Device
        """
        if key in self.keys:
            raise DuplicateError(f"It is forbidden to supply duplicate keys: '{key}'")
        if isinstance(key, ProductId):
            type = DeviceKeyType.PRODUCT_ID
        elif isinstance(key, AccreditedSystemId):
            type = DeviceKeyType.ACCREDITED_SYSTEM_ID
        else:
            raise InvalidDeviceKeyError(
                "key must be ProductId() or AccreditedSystemId()"
            )
        device_key = DeviceKey(type=type)
        event = DeviceKeyAddedEvent(id=self.id, key=key, **device_key.dict())
        self.keys[key] = device_key
        return self.add_event(event=event)

    # def add_page(
    #     self, index: str = "", values: dict[str, DevicePageValue] = None
    # ) -> DevicePage:
    #     """
    #     Create a page for storing values
    #     """
    #     if not re.match(PAGE_NAME_REGEX, index):
    #         raise InvalidKeyError(f"Invalid page index: {index}")
    #     if index in self.pages:
    #         raise DuplicateError(f"It is forbidden to supply duplicate pages: {index}")
    #     page = DevicePage(values=values or {})
    #     self.add_event(DevicePageAddedEvent(id=self.id, page=index))
    #     self.pages[index] = page
    #     return page

    # def remove_page(self, index: str = ""):
    #     """
    #     Remove a page from the device
    #     """
    #     if index not in self.pages:
    #         raise NotFoundError(f"Unknown page: {index}")
    #     self.add_event(DevicePageRemovedEvent(id=self.id, page=index))
    #     del self.pages[index]

    # def get_page(self, index: str = "") -> DevicePage:
    #     """
    #     Retrieve a single page
    #     """
    #     if index not in self.pages:
    #         raise NotFoundError(f"Unknown page: {index}")
    #     return self.pages[index]

    # def set_values(self, values: dict[str, DevicePageValue], page: str = None):
    #     """
    #     Update the values on a page
    #     """
    #     device_page = self.get_page(page or "")
    #     device_page.values = {**device_page.values, **values}
    #     self.add_event(DevicePageUpdatedEvent(id=self.id, page=page))

    # def add_relationship(
    #     self, target: "Device", type: RelationshipType
    # ) -> RelationshipAddedEvent:
    #     """
    #     Adds a relationship between two Devices
    #     """
    #     if target.id in self.relationships:
    #         raise DuplicateError(
    #             f"It is forbidden to supply duplicate relationships: '{target.id}'"
    #         )
    #     relationship = Relationship(type=type)
    #     event = RelationshipAddedEvent(
    #         id=self.id, target=target.id, **relationship.dict()
    #     )
    #     self.relationships[target.id] = relationship
    #     return self.add_event(event=event)

    # def remove_relationship(self, target: str) -> RelationshipRemovedEvent:
    #     """
    #     Removes an existing relationship between two Devices
    #     TODO: Do we delete them or mark them inactive?
    #     """
    #     target_id = target.id if isinstance(target, Device) else target
    #     if target_id not in self.relationships:
    #         raise NotFoundError(f"Relationship {target_id} is unknown")
    #     del self.relationships[target_id]
    #     event = RelationshipRemovedEvent(id=self.id, target=target_id)
    #     return self.add_event(event=event)

    # def remove_key(self, key: str) -> DeviceKeyRemovedEvent:
    #     """
    #     Remove an existing key from a Device
    #     TODO: Do we delete them or mark inactive?
    #     """
    #     if key not in self.keys:
    #         raise NotFoundError(f"Key {key} is unknown")
    #     del self.keys[key]
    #     event = DeviceKeyRemovedEvent(id=self.id, key=key)
    #     return self.add_event(event=event)

    # def delete(self) -> list[Event]:
    #     """
    #     Delete the entire Device and all sub-entities.
    #     This method will generate all the events required to ensure that all
    #     associated records are removed.
    #     """
    #     events = (
    #         [
    #             self.remove_relationship(target)
    #             for target in list(self.relationships.keys())
    #         ]
    #         + [self.remove_key(key) for key in list(self.keys.keys())]
    #         + [DeviceDeletedEvent(id=self.id)]
    #     )
    #     self.events = self.events + events
    #     return self.events


# class RelationshipType(StrEnum):
#     """
#     How we classify the relationships between two devices.
#     """

#     DEPENDENCY = auto()
#     # Device is dependent upon / consumes another Device
#     # https://nhsd-confluence.digital.nhs.uk/display/SPINE/CPM+Domain+Model#CPMDomainModel-Dependencies
#     COMPONENT = auto()
#     # Device is a sub-component of an existing Device
#     # https://nhsd-confluence.digital.nhs.uk/display/SPINE/CPM+Domain+Model#CPMDomainModel-Ranges
#     REVISION = auto()
#     # Device is a revision of an existing Device
#     # https://nhsd-confluence.digital.nhs.uk/display/SPINE/CPM+Domain+Model#CPMDomainModel-Versioning


# class Relationship(BaseModel):
#     """
#     A relationship indicates that two Devices are linked.  One device is the "Source" and the other is the "Destination"
#     """

#     type: RelationshipType


# @dataclass(kw_only=True, slots=True)
# class DeviceKeyRemovedEvent(Event):
#     id: UUID
#     key: ProductId | AccreditedSystemId


# @dataclass(kw_only=True, slots=True)
# class DeviceUpdatedEvent(Event):
#     id: UUID
#     name: str
#     type: "DeviceType"


# @dataclass(kw_only=True, slots=True)
# class DeviceDeletedEvent(Event):
#     id: UUID


# @dataclass(kw_only=True, slots=True)
# class RelationshipAddedEvent(Event):
#     id: UUID
#     target: UUID
#     type: "RelationshipType"


# @dataclass(kw_only=True, slots=True)
# class RelationshipRemovedEvent(Event):
#     id: UUID
#     target: UUID


# @dataclass(kw_only=True, slots=True)
# class DevicePageAddedEvent(Event):
#     id: UUID
#     page: str


# @dataclass(kw_only=True, slots=True)
# class DevicePageUpdatedEvent(Event):
#     id: UUID
#     page: str


# @dataclass(kw_only=True, slots=True)
# class DevicePageRemovedEvent(Event):
#     id: UUID
#     page: str


# PAGE_NAME_REGEX = r"^([A-z0-9]+(_[A-z0-9]+)*)(\:[A-z0-9]+(_[A-z0-9]+)*)?$"
# VALUE_NAME_REGEX = r"^([A-z0-9]+(_[A-z0-9]+)*)(\:[A-z0-9]+(_[A-z0-9]+)*)?$"


# DevicePageValue = int | float | bool | str


# class DevicePage(BaseModel):
#     values: dict[str, DevicePageValue] = Field(default_factory=dict)

#     def add_value(self, name: str, value: any):
#         if not re.match(VALUE_NAME_REGEX, name):
#             raise InvalidKeyError(f"Invalid name: {name}")
#         self.values[name] = value

#     def set_value(self, name: str, value: DevicePageValue):
#         if name not in self.values:
#             raise NotFoundError(f"Unknown value: {name}")
#         self.values[name] = value

#     def get_value(self, name: str) -> DevicePageValue:
#         if name not in self.values:
#             raise NotFoundError(f"Unknown value: {name}")
#         return self.values[name]

#     def remove_value(self, name: str):
#         if name not in self.values:
#             raise NotFoundError(f"Unknown value: {name}")
#         del self.values[name]
