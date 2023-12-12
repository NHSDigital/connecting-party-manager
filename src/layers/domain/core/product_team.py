from dataclasses import dataclass
from uuid import UUID

from pydantic import Field

from .aggregate_root import AggregateRoot
from .device import Device, DeviceCreatedEvent, DeviceStatus, DeviceType
from .event import Event
from .validation import ENTITY_NAME_REGEX


@dataclass(kw_only=True, slots=True)
class ProductTeamCreatedEvent(Event):
    id: UUID
    name: str
    ods_code: str


@dataclass(kw_only=True, slots=True)
class ProductTeamDeletedEvent(Event):
    id: UUID


class ProductTeam(AggregateRoot):
    """
    A ProductTeam is the entity that owns Products, and is derived from ODS
    Organisations.  A single ODS Organisation can be mapped onto multiple
    ProductTeams, meaning that `ods_code` is not unique amongst ProductTeams.
    """

    id: UUID
    name: str = Field(regex=ENTITY_NAME_REGEX)
    ods_code: str

    def create_device(
        self,
        id: UUID,
        name: str,
        type: DeviceType,
        status: DeviceStatus = DeviceStatus.ACTIVE,
    ) -> Device:
        device = Device(
            id=id,
            name=name,
            type=type,
            status=status,
            product_team_id=self.id,
            ods_code=self.ods_code,
        )
        device_created_event = DeviceCreatedEvent(**device.dict())
        device.add_event(device_created_event)
        self.add_event(device_created_event)
        return device

    def delete(self) -> list[Event]:
        return [ProductTeamDeletedEvent(id=self.id)]
