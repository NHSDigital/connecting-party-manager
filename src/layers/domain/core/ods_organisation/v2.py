from uuid import UUID

from domain.core.aggregate_root import AggregateRoot
from domain.core.product_team.v2 import ProductTeam, ProductTeamCreatedEvent
from domain.core.validation import ODS_CODE_REGEX
from pydantic import Field


class OdsOrganisation(AggregateRoot):
    """
    An object that maps onto the Organisational Data Service (ODS) definition
    of an "Organisation".  We are only interested in a sub-set of the fields
    they hold.
    """

    ods_code: str = Field(regex=ODS_CODE_REGEX)

    def create_product_team(self, id: UUID, name: str) -> ProductTeam:
        product_team = ProductTeam(id=id, name=name, ods_code=self.ods_code)
        event = ProductTeamCreatedEvent(**product_team.dict())
        product_team.add_event(event)
        self.add_event(event=event)
        return product_team
