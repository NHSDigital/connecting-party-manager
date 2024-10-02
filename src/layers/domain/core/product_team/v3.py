from uuid import UUID

from attr import dataclass
from domain.core.aggregate_root import AggregateRoot
from domain.core.cpm_product import CpmProduct, CpmProductCreatedEvent
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

    def create_cpm_product(self, name: str, product_id: str = None) -> CpmProduct:
        extra_kwargs = {"id": product_id} if product_id is not None else {}
        product = CpmProduct(
            product_team_id=self.id, name=name, ods_code=self.ods_code, **extra_kwargs
        )
        product_created_event = CpmProductCreatedEvent(**product.dict(exclude={"keys"}))
        product.add_event(product_created_event)
        self.add_event(product_created_event)
        return product
