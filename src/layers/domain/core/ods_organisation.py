from domain.events.product_team_created_event import ProductTeamCreatedEvent

from layers.domain.core.common import assert_is_ods_code

from .entity import Entity
from .product_team import ProductTeam
from .user import User


class OdsOrganisation(Entity[str]):
    """
    Represents the bare minimum properties that we need to take from the
    ODS definition of an organisation.
    """

    def __init__(
        self,
        id: str,
        name: str,
    ):
        assert_is_ods_code(id)
        super().__init__(id, name)

    def create_product_team(
        self, id: str, name: str, owner: User
    ) -> (ProductTeam, ProductTeamCreatedEvent):
        """
        Creates an instance of a ProductTeam
        """
        assert isinstance(owner, User), "owner is required"
        result = ProductTeam(id, name, self.as_reference(), owner.as_reference())
        event = ProductTeamCreatedEvent(
            id, name, self.as_reference(), owner.as_reference()
        )
        return (result, event)
