from datetime import datetime
from typing import Optional
from uuid import UUID

from attr import dataclass
from domain.core.aggregate_root import AggregateRoot
from domain.core.event import Event
from domain.core.timestamp import now
from domain.core.validation import PRODUCT_NAME_REGEX
from pydantic import BaseModel, Extra, Field


class CpmProductIncomingParams(BaseModel, extra=Extra.forbid):
    product_team_id: UUID = Field(...)
    product_name: str = Field(regex=PRODUCT_NAME_REGEX, min_length=1)


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

    id: str  # product_id
    product_team_id: UUID = Field(...)
    name: str = Field(regex=PRODUCT_NAME_REGEX, min_length=1)
    ods_code: str
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: Optional[datetime] = Field(default=None)
    deleted_on: Optional[datetime] = Field(default=None)
