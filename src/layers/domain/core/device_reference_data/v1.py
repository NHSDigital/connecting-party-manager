from datetime import datetime
from uuid import UUID, uuid4

from attr import dataclass
from domain.core.aggregate_root import AggregateRoot
from domain.core.cpm_system_id.v1 import ProductId
from domain.core.event import Event
from domain.core.timestamp import now
from domain.core.validation import DEVICE_NAME_REGEX
from pydantic import Field


@dataclass(kw_only=True, slots=True)
class DeviceReferenceDataCreatedEvent(Event):
    id: str
    name: str
    product_id: ProductId
    product_team_id: UUID
    ods_code: str
    created_on: str
    updated_on: str = None
    deleted_on: str = None


class DeviceReferenceData(AggregateRoot):
    """An object to hold boilerplate Device QuestionnaireResponses"""

    id: UUID = Field(default_factory=uuid4, immutable=True)
    name: str = Field(regex=DEVICE_NAME_REGEX)
    product_id: ProductId = Field(immutable=True)
    product_team_id: str = Field(immutable=True)
    ods_code: str = Field(immutable=True)
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: datetime = Field(default=None)
    deleted_on: datetime = Field(default=None)