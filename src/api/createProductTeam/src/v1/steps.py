from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.fhir.r4 import Organization  # StrictOrganization
from event.step_chain import StepChain


def _parse_fhir_organisation(organisation: dict) -> Organization:
    org = Organization(**organisation)

    # TODO: Also need to validate against StrictOrganization here
    # strict_org = StrictOrganization(**organisation)
    return org


def parse_fhir_organisation(data, cache) -> Organization:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return _parse_fhir_organisation(organisation=event.json_body)


def set_http_status(data, cache) -> HTTPStatus:
    return HTTPStatus.CREATED


steps = [
    parse_fhir_organisation,
    set_http_status,
]
