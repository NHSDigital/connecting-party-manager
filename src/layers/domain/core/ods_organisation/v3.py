from domain.core.aggregate_root import AggregateRoot
from domain.core.product_team.v3 import ProductTeam, ProductTeamCreatedEvent
from domain.core.validation import ODS_CODE_REGEX
from pydantic import Field


class OdsOrganisation(AggregateRoot):
    """
    An object that maps onto the Organisational Data Service (ODS) definition
    of an "Organisation".  We are only interested in a sub-set of the fields
    they hold.
    """

    ods_code: str = Field(regex=ODS_CODE_REGEX)

    def create_product_team(self, name: str = "", keys: list = []) -> ProductTeam:
        product_team = ProductTeam(name=name, ods_code=self.ods_code, keys=keys)
        event = ProductTeamCreatedEvent(**product_team.dict())
        product_team.add_event(event)
        self.add_event(event=event)
        return product_team
