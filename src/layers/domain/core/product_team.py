from uuid import UUID

from .entity import Entity
from .product import Product
from .reference import Reference


class ProductTeam(Entity[UUID]):
    """
    A ProductTeam is created from a Supplier OdsOrganisation, and is the entity
    that creates and owns Products.
    """

    def __init__(
        self,
        id: UUID,
        name: str,
        organisation: Reference,
        owner: Reference,
    ):
        super().__init__(id, name)
        self.organisation = organisation
        self.owner = owner

    def create_product(self) -> Product:
        """
        Creates an instance of a new Product
        """
        pass
