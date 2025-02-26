from domain.core.aggregate_root import AggregateRoot
from domain.core.product_team import ProductTeam, ProductTeamCreatedEvent
from domain.core.product_team_epr import ProductTeam as ProductTeamEpr
from domain.core.product_team_epr import (
    ProductTeamCreatedEvent as ProductTeamCreatedEventEpr,
)
from domain.core.validation import ODS_CODE_REGEX
from pydantic import Field


class OdsOrganisation(AggregateRoot):
    """
    An object that maps onto the Organisational Data Service (ODS) definition
    of an "Organisation".  We are only interested in a sub-set of the fields
    they hold.
    """

    ods_code: str = Field(regex=ODS_CODE_REGEX)

    def create_product_team(self, name: str, keys: list = None) -> ProductTeam:
        keys = keys or []
        product_team = ProductTeam(name=name, ods_code=self.ods_code, keys=keys)
        event = ProductTeamCreatedEvent(**product_team.state())
        product_team.add_event(event)
        self.add_event(event=event)
        return product_team

    def create_product_team_epr(self, name: str, keys: list = None) -> ProductTeamEpr:
        keys = keys or []
        product_team = ProductTeamEpr(name=name, ods_code=self.ods_code, keys=keys)
        event = ProductTeamCreatedEventEpr(**product_team.state())
        product_team.add_event(event)
        self.add_event(event=event)
        return product_team
