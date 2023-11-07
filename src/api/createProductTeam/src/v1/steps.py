from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.product import ProductTeam, ProductTeamCreatedEvent
from domain.core.root import Root
from event.step_chain import StepChain


def _create_product_team(
    event: APIGatewayProxyEvent,
) -> tuple[ProductTeam, ProductTeamCreatedEvent]:
    _product_team: dict = event.json_body
    _user = _product_team.pop("owner")
    _organisation = _product_team.pop("organisation")

    user = Root.create_user(**_user)
    organisation = Root.create_ods_organisation(**_organisation)
    product_team, product_team_creation_event = organisation.create_product_team(
        owner=user, **_product_team
    )
    return product_team, product_team_creation_event


def create_product_team(data, cache) -> tuple[ProductTeam, ProductTeamCreatedEvent]:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return _create_product_team(event=event)


def set_http_status(data, cache) -> HTTPStatus:
    return HTTPStatus.CREATED


steps = [
    create_product_team,
    set_http_status,
]
