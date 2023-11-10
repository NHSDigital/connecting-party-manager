from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.product_team import ProductTeam, ProductTeamCreatedEvent
from domain.core.root import Root
from domain.fhir.r4 import Organization  # StrictOrganization
from event.step_chain import StepChain


def _parse_fhir_organisation(organisation: dict) -> Organization:
    org = Organization(**organisation)

    # TODO: Also need to validate against StrictOrganization here
    # strict_org = StrictOrganization(**organisation)
    return org


def _create_product_team(
    event: APIGatewayProxyEvent,
) -> tuple[ProductTeam, ProductTeamCreatedEvent]:
    _product_team: dict = event.json_body

    organisation = Root.create_ods_organisation(
        ods_code=_product_team["ods_code"], name="Test"
    )
    product_team = organisation.create_product_team(
        id=_product_team["id"],
        name=_product_team["name"],
    )
    return product_team


def parse_fhir_organisation(data, cache) -> Organization:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return _parse_fhir_organisation(organisation=event.json_body)


def set_http_status(data, cache) -> HTTPStatus:
    return HTTPStatus.CREATED


steps = [
    parse_fhir_organisation,
    set_http_status,
]
