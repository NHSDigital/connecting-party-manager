from datetime import datetime

from attr import dataclass
from domain.core import event
from domain.core.aggregate_root import AggregateRoot
from domain.core.cpm_system_id.v1 import ProductId
from domain.core.device.v3 import UPDATED_ON, Device, DeviceCreatedEvent, event
from domain.core.device_reference_data.v1 import (
    DeviceReferenceData,
    DeviceReferenceDataCreatedEvent,
)
from domain.core.enum import Status
from domain.core.error import DuplicateError
from domain.core.event import Event
from domain.core.product_key.v1 import ProductKey
from domain.core.timestamp import now
from domain.core.validation import CPM_PRODUCT_NAME_REGEX
from pydantic import Field


@dataclass(kw_only=True, slots=True)
class CpmProductCreatedEvent(Event):
    id: str
    product_team_id: str
    name: str
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: str = None


@dataclass(kw_only=True, slots=True)
class CpmProductKeyAddedEvent(Event):
    new_key: ProductKey
    id: str
    product_team_id: str
    name: str
    ods_code: str
    status: Status
    created_on: str
    updated_on: str = None
    deleted_on: str = None
    keys: list[ProductKey]


@dataclass(kw_only=True, slots=True)
class CpmProductDeletedEvent(Event):
    id: str
    product_team_id: str
    name: str
    ods_code: str
    status: Status
    created_on: str
    updated_on: str
    deleted_on: str
    keys: list[ProductKey]


class CpmProduct(AggregateRoot):
    """
    A product in the database.
    """

    id: ProductId = Field(default_factory=ProductId.create)
    product_team_id: str = Field(...)
    name: str = Field(regex=CPM_PRODUCT_NAME_REGEX, min_length=1)
    ods_code: str
    status: Status = Status.ACTIVE
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: datetime = Field(default=None)
    deleted_on: datetime = Field(default=None)
    keys: list[ProductKey] = Field(default_factory=list)

    def create_device(
        self,
        name: str,
        status: Status = Status.ACTIVE,
    ) -> Device:
        device = Device(
            name=name,
            product_team_id=self.product_team_id,
            product_id=self.id,
            ods_code=self.ods_code,
            status=status,
        )
        device_created_event = DeviceCreatedEvent(**device.dict())
        self.add_event(device_created_event)
        device.add_event(device_created_event)
        return device

    def create_device_reference_data(self, name: str) -> DeviceReferenceData:
        device_reference_data = DeviceReferenceData(
            name=name,
            product_id=self.id,
            product_team_id=self.product_team_id,
            ods_code=self.ods_code,
        )
        event = DeviceReferenceDataCreatedEvent(
            **device_reference_data.dict(exclude={"questionnaire_responses"})
        )
        self.add_event(event)
        device_reference_data.add_event(event)
        return device_reference_data

    @event
    def add_key(self, key_type: str, key_value: str) -> CpmProductKeyAddedEvent:
        product_key = ProductKey(key_value=key_value, key_type=key_type)
        if product_key in self.keys:
            raise DuplicateError(
                f"It is forbidden to supply duplicate keys: '{key_type}':'{key_value}'"
            )
        self.keys.append(product_key)
        product_data = self.state()
        product_data.pop(UPDATED_ON)  # The @event decorator will handle updated_on
        return CpmProductKeyAddedEvent(new_key=product_key, **product_data)

    @event
    def delete(self):
        deleted_on = now()
        product_data = self._update(
            data=dict(
                status=Status.INACTIVE, updated_on=deleted_on, deleted_on=deleted_on
            )
        )
        return CpmProductDeletedEvent(**product_data)
