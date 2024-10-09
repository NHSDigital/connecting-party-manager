from datetime import datetime
from uuid import uuid4

from attr import dataclass

# from domain.core import event
from domain.core.aggregate_root import AggregateRoot
from domain.core.cpm_product import CpmProduct, CpmProductCreatedEvent

# from domain.core.device.v2 import UPDATED_ON, event
from domain.core.enum import Status

# from domain.core.error import DuplicateError
from domain.core.event import Event
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


# @dataclass(kw_only=True, slots=True)
# class CpmProductTeamKeyAddedEvent(Event):
#     new_key: ProductTeamKey
#     id: str
#     name: str
#     ods_code: str
#     status: Status
#     created_on: str
#     updated_on: str = None
#     deleted_on: str = None
#     keys: list[ProductTeamKey]


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
        if values.get("id") is None:
            ods_code = values.get("ods_code")
            if ods_code:
                values["id"] = f"{ods_code}.{uuid4()}"
        return values

    # @event
    # def add_key(self, key_type: str, key_value: str) -> CpmProductTeamKeyAddedEvent:
    #     product_team_key = ProductTeamKey(key_value=key_value, key_type=key_type)
    #     if product_team_key in self.keys:
    #         raise DuplicateError(
    #             f"It is forbidden to supply duplicate keys: '{key_type}':'{key_value}'"
    #         )
    #     self.keys.append(product_team_key)
    #     product_team_data = self.state()
    #     product_team_data.pop(UPDATED_ON)  # The @event decorator will handle updated_on
    #     return CpmProductTeamKeyAddedEvent(new_key=product_team_key, **product_team_data)

    def create_cpm_product(self, name: str, product_id: str = None) -> CpmProduct:
        extra_kwargs = {"id": product_id} if product_id is not None else {}
        product = CpmProduct(
            product_team_id=self.id, name=name, ods_code=self.ods_code, **extra_kwargs
        )
        product_created_event = CpmProductCreatedEvent(**product.dict(exclude={"keys"}))
        product.add_event(product_created_event)
        self.add_event(product_created_event)
        return product
