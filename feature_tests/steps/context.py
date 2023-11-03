from dataclasses import dataclass

from behave.model import Table
from behave.runner import Context as BehaveContext
from domain.core.product import OdsOrganisation
from domain.core.questionnaire import Questionnaire
from domain.core.user import User
from domain.events.event import Event


@dataclass
class Context(BehaveContext):
    # Extra domain specific fields
    questionnaires: dict[str, Questionnaire]
    users: dict[str, User]
    ods_organisations: dict[str, OdsOrganisation]
    events: list[Event]
    error: list
    result: any
    subject: any

    # Standard behave fields
    table: Table
