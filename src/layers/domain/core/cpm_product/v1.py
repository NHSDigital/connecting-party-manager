from datetime import datetime
from uuid import UUID

from attr import dataclass
from domain.core.aggregate_root import AggregateRoot
from domain.core.device.v2 import UPDATED_ON, event
from domain.core.error import DuplicateError
from domain.core.event import Event
from domain.core.product_key.v1 import ProductKey
from domain.core.timestamp import now
from domain.core.validation import PRODUCT_NAME_REGEX
from pydantic import BaseModel, Extra, Field


class CpmProductIncomingParams(BaseModel, extra=Extra.forbid):
    product_name: str = Field(regex=PRODUCT_NAME_REGEX, min_length=1)


@dataclass(kw_only=True, slots=True)
class CpmProductCreatedEvent(Event):
    id: str
    product_team_id: UUID
    name: str
    ods_code: str
    created_on: str
    updated_on: str = None
    deleted_on: str = None


@dataclass(kw_only=True, slots=True)
class CpmProductKeyAddedEvent(Event):
    new_key: ProductKey
    id: str
    product_team_id: UUID
    name: str
    ods_code: str
    created_on: str
    updated_on: str = None
    deleted_on: str = None
    keys: list[ProductKey]


class CpmProduct(AggregateRoot):
    """
    A product in the database.
    """

    id: str  # product_id
    product_team_id: UUID = Field(...)
    name: str = Field(regex=PRODUCT_NAME_REGEX, min_length=1)
    ods_code: str
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: datetime = Field(default=None)
    deleted_on: datetime = Field(default=None)
    keys: list[ProductKey] = Field(default_factory=list)

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
