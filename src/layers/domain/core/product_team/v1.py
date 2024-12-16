from datetime import datetime

from attr import dataclass
from domain.core.aggregate_root import AggregateRoot
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
    updated_on: str = None
    deleted_on: str = None
    keys: list[ProductTeamKey] = Field(default_factory=list)


class ProductTeam(AggregateRoot):
    """
    A ProductTeam is the entity that owns Products, and is derived from ODS
    Organisations.  A single ODS Organisation can be mapped onto multiple
    ProductTeams, meaning that `ods_code` is not unique amongst ProductTeams.
    """

    id: str = None
    name: str = Field(regex=ENTITY_NAME_REGEX)
    ods_code: str
    status: Status = Status.ACTIVE
    created_on: datetime = Field(default_factory=now, immutable=True)
    updated_on: datetime = Field(default=None)
    deleted_on: datetime = Field(default=None)
    keys: list[ProductTeamKey] = Field(default_factory=list)

    @root_validator(pre=True)
    def set_id(cls, values):
        ods_code = values.get("ods_code")
        if ods_code and not values.get("id"):
            product_team = ProductTeamId.create(ods_code=ods_code)
            values["id"] = product_team.id
        return values

    def create_cpm_product(self, name: str, product_id: str = None) -> CpmProduct:
        extra_kwargs = {"id": product_id} if product_id is not None else {}
        product = CpmProduct(
            product_team_id=self.id, name=name, ods_code=self.ods_code, **extra_kwargs
        )
        data = product.state()
        del data["keys"]
        product_created_event = CpmProductCreatedEvent(**data)
        product.add_event(product_created_event)
        return product


class ProductTeamEventDeserializer(EventDeserializer):
    event_types = (ProductTeamCreatedEvent,)
