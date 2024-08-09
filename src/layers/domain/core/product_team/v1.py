from uuid import UUID

from attr import dataclass
from domain.core.aggregate_root import AggregateRoot
from domain.core.device import Device, DeviceCreatedEvent, DeviceStatus, DeviceType
from domain.core.event import Event
from domain.core.validation import ENTITY_NAME_REGEX
from pydantic import Field


@dataclass(kw_only=True, slots=True)
class ProductTeamCreatedEvent(Event):
    id: UUID
    name: str
    ods_code: str


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
        name: str,
        type: DeviceType,
        status: DeviceStatus = DeviceStatus.ACTIVE,
        _trust=False,
    ) -> Device:
        device = Device(
            name=name,
            type=type,
            status=status,
            product_team_id=self.id,
            ods_code=self.ods_code,
        )
        device_created_event = DeviceCreatedEvent(**device.dict(), _trust=_trust)
        device.add_event(device_created_event)
        self.add_event(device_created_event)
        return device
