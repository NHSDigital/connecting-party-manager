from dataclasses import dataclass

from behave.model import Table
from behave.runner import Context as BehaveContext
from domain.core.ods_organisation import OdsOrganisation
from domain.core.product_team import ProductTeam
from domain.core.questionnaire import Questionnaire
from domain.events.event import Event


@dataclass
class Context(BehaveContext):
    # Extra domain specific fields
    questionnaires: dict[str, Questionnaire]
    questionnaire_response: list[tuple[str, list]]
    ods_organisations: dict[str, OdsOrganisation]
    product_teams: dict[str, ProductTeam]
    events: list[Event]
    error: list
    result: any
    subject: any

    # Standard behave fields
    table: Table
