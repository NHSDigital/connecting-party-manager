from datetime import datetime
from typing import Optional

from attr import dataclass
from domain.core.aggregate_root import AggregateRoot, event
from domain.core.cpm_product import CpmProduct, CpmProductCreatedEvent
from domain.core.cpm_system_id import ProductTeamId
from domain.core.enum import Status
from domain.core.event import Event, EventDeserializer
from domain.core.product_team_key import ProductTeamKey
from domain.core.timestamp import now
from domain.core.validation import ENTITY_NAME_REGEX
from pydantic import Field, root_validator


@dataclass(kw_only=True, slots=True)
class ProductTeamCreatedEvent(Event):
    id: str
    name: str
    ods_code: str
    status: Status
    created_on: str
    updated_on: Optional[str]
    deleted_on: Optional[str]
    keys: list[ProductTeamKey] = Field(default_factory=list)


@dataclass(kw_only=True, slots=True)
class ProductTeamDeletedEvent(Event):
    id: str
    name: str
    ods_code: str
    status: Status
    created_on: str
    updated_on: str
    deleted_on: str
    keys: list[ProductTeamKey] = Field(default_factory=list)


class ProductTeam(AggregateRoot):
    """
    A ProductTeam is the entity that owns Products, and is derived from ODS
    Organisations.  A single ODS Organisation can be mapped onto multiple
    ProductTeams, meaning that `ods_code` is not unique amongst ProductTeams.
    """

    id: Optional[str]
    name: str = Field(regex=ENTITY_NAME_REGEX)
    ods_code: str
    status: Status = Status.ACTIVE
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: datetime = Field(default=None)
    deleted_on: datetime = Field(default=None)
    keys: list[ProductTeamKey] = Field(default_factory=list)

    @root_validator(pre=True)
    def set_id(cls, values):
        if not values.get("id"):
            product_team = ProductTeamId.create()
            values["id"] = product_team.id
        return values

    def create_cpm_product(self, name: str, product_id: str = None) -> CpmProduct:
        extra_kwargs = {"id": product_id} if product_id is not None else {}
        product_team_id = next(
            (key.key_value for key in self.keys if key.key_type == "product_team_id"),
            None,
        )
        product = CpmProduct(
            cpm_product_team_id=self.id,
            product_team_id=product_team_id,
            name=name,
            ods_code=self.ods_code,
            **extra_kwargs
        )
        data = product.state()
        del data["keys"]
        product_created_event = CpmProductCreatedEvent(**data)
        product.add_event(product_created_event)
        return product

    @event
    def delete(self):
        deleted_on = now()
        product_team_data = self._update(
            data=dict(
                status=Status.INACTIVE, updated_on=deleted_on, deleted_on=deleted_on
            )
        )
        return ProductTeamDeletedEvent(**product_team_data)


class ProductTeamEventDeserializer(EventDeserializer):
    event_types = (ProductTeamCreatedEvent, ProductTeamDeletedEvent)
