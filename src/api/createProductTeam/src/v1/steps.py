from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.fhir_transform import create_product_team_from_fhir_org_json
from domain.core.product_team import ProductTeam
from domain.ods import validate_ods_code
from event.response.validation_errors import mark_json_decode_errors_as_inbound
from event.step_chain import StepChain
from repository.product_team_repo import ProductTeamRepository


@mark_json_decode_errors_as_inbound
def parse_event_body(data, cache) -> dict:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return event.json_body if event.body else {}


def create_product_team(data, cache) -> ProductTeam:
    json_body = data[parse_event_body]
    product_team = create_product_team_from_fhir_org_json(fhir_org_json=json_body)
    return product_team


def validate_product_team_ods_code(data, cache) -> None:
    product_team: ProductTeam = data[create_product_team]
    validate_ods_code(ods_code=product_team.ods_code)


def save_product_team(data, cache) -> dict:
    product_team = data[create_product_team]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.write(entity=product_team)


def set_http_status(data, cache) -> HTTPStatus:
    return HTTPStatus.CREATED


steps = [
    parse_event_body,
    create_product_team,
    validate_product_team_ods_code,
    save_product_team,
    set_http_status,
]
