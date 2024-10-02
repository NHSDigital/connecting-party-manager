from datetime import datetime
from typing import Optional
from uuid import UUID

from attr import dataclass
from domain.core.aggregate_root import AggregateRoot
from domain.core.cpm_system_id.v1 import ProductId
from domain.core.event import Event
from domain.core.timestamp import now
from domain.core.validation import CPM_PRODUCT_NAME_REGEX
from pydantic import Field


@dataclass(kw_only=True, slots=True)
class CpmProductCreatedEvent(Event):
    id: str
    product_team_id: UUID
    name: str
    ods_code: str
    created_on: str
    updated_on: Optional[str] = None
    deleted_on: Optional[str] = None


class CpmProduct(AggregateRoot):
    """
    A product in the database.
    """

    id: ProductId = Field(default_factory=ProductId.create)
    product_team_id: UUID = Field(...)
    name: str = Field(regex=CPM_PRODUCT_NAME_REGEX, min_length=1)
    ods_code: str
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: Optional[datetime] = Field(default=None)
    deleted_on: Optional[datetime] = Field(default=None)
