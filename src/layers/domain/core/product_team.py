from uuid import UUID

from domain.core.aggregate_root import AggregateRoot
from domain.core.event import Event
from domain.core.product import Product, ProductCreatedEvent, ProductStatus, ProductType
from domain.core.validation import ENTITY_NAME_REGEX
from pydantic import Field


class ProductTeamCreatedEvent(Event):
    """
    Raised when a new ProductTeam has been created within the domain.
    """

    def __init__(self, id, name, ods_code):
        self.id = id
        self.name = name
        self.ods_code = ods_code


class ProductTeamDeletedEvent(Event):
    """
    Raised when an existing ProductTeam has been deleted.
    """

    def __init__(self, id):
        self.id = id


class ProductTeam(AggregateRoot):
    """
    A ProductTeam is the entity that owns Products, and is derived from ODS
    Organisations.  A single ODS Organisation can be mapped onto multiple
    ProductTeams, meaning that `ods_code` is not unique amongst ProductTeams.
    """

    id: UUID
    name: str = Field(regex=ENTITY_NAME_REGEX)
    ods_code: str

    def create_product(
        self,
        id: UUID,
        name: str,
        type: ProductType,
        status: ProductStatus = ProductStatus.ACTIVE,
    ) -> Product:
        event = ProductCreatedEvent(
            id=id,
            name=name,
            type=type,
            product_team_id=self.id,
            ods_code=self.ods_code,
            status=status,
        )
        result = Product(
            id=id,
            name=name,
            type=type,
            status=status,
            product_team_id=self.id,
            ods_code=self.ods_code,
            events=[event],
        )
        return result

    def delete(self) -> list[Event]:
        return [ProductTeamDeletedEvent(id=self.id)]
