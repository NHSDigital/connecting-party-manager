"""
The collection of models required to create Products:

OdsOrganisation -creates-> ProductTeam -creates-> Product
                ∟ emits -> ProductTeamCreatedEvent
"""
from typing import Iterable, TypeVar
from uuid import UUID

from domain.events.event import Event

from .entity import Entity
from .questionnaire_entity import QuestionnaireEntity
from .user import User
from .validation import (
    validate_ods_code,
    validate_product_id_or_asid,
    validate_type,
    validate_uuid,
)

SetType = TypeVar("SetType")


def default_set(iterable: Iterable[SetType]) -> set[SetType]:
    return set(iterable if iterable is not None else [])


class OdsOrganisation(Entity[str]):
    """
    Represents the bare minimum properties that we need to take from the
    ODS definition of an organisation.
    """

    def __init__(self, id: str, name: str):
        validate_ods_code(ods_code=id)

        super().__init__(id=id, name=name)

    def create_product_team(
        self, id: str, name: str, owner: User
    ) -> tuple["ProductTeam", "ProductTeamCreatedEvent"]:
        """
        Creates an instance of a ProductTeam
        """
        product_team = ProductTeam(id=id, name=name, organisation=self, owner=owner)
        event = ProductTeamCreatedEvent(product_team=product_team)
        return (product_team, event)


class ProductTeam(Entity[UUID]):
    """
    A ProductTeam is created from a Supplier OdsOrganisation, and is the entity
    that creates and owns Products.
    """

    def __init__(self, id: UUID, name: str, organisation: OdsOrganisation, owner: User):
        validate_uuid(uuid=id)
        validate_type(obj=organisation, expected_type=OdsOrganisation)
        validate_type(obj=owner, expected_type=User)

        super().__init__(id=id, name=name)
        self.organisation = organisation
        self.owner = owner

    def create_product(self) -> "Product":
        """
        Creates an instance of a new Product
        """
        pass


class Product(Entity[UUID], QuestionnaireEntity):
    """
    A Product represents logical and physical software products.  A Product may
    be referenced by multiple keys, such as internal GUID, Product Id, ASID,
    etc.
    """

    def __init__(
        self,
        id: str,
        name: str,
        questionnaires: set[str] = None,
        dependency_questionnaires: set[str] = None,
    ):
        validate_product_id_or_asid(id=id)

        super().__init__(id=id, name=name)
        self._questionnaires = default_set(questionnaires)
        self._dependency_questionnaires = default_set(dependency_questionnaires)


class ProductTeamCreatedEvent(Event):
    def __init__(self, product_team: ProductTeam):
        validate_type(obj=product_team, expected_type=ProductTeam)

        self.product_team = product_team
