from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.product_team_epr import ProductTeam
from domain.core.root import Root
from domain.ods import validate_ods_code
from domain.repository.product_team_epr_repository import ProductTeamRepository
from domain.request_models import CreateProductTeamIncomingParams
from domain.response.validation_errors import (
    mark_json_decode_errors_as_inbound,
    mark_validation_errors_as_inbound,
)
from event.step_chain import StepChain


@mark_json_decode_errors_as_inbound
def parse_event_body(data, cache) -> dict:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return event.json_body if event.body else {}


@mark_validation_errors_as_inbound
def parse_incoming_product_team(data, cache) -> CreateProductTeamIncomingParams:
    json_body = data[parse_event_body]
    incoming_product_team = CreateProductTeamIncomingParams(**json_body)
    return incoming_product_team


def validate_product_team_ods_code(data, cache) -> None:
    product_team_params: CreateProductTeamIncomingParams = data[
        parse_incoming_product_team
    ]
    validate_ods_code(ods_code=product_team_params.ods_code)


def create_product_team(data, cache) -> ProductTeam:
    product_team_params: CreateProductTeamIncomingParams = data[
        parse_incoming_product_team
    ]
    org = Root.create_ods_organisation(ods_code=product_team_params.ods_code)
    product_team = org.create_product_team_epr(
        **product_team_params.dict(exclude={"ods_code"})
    )
    return product_team


def save_product_team(data, cache) -> dict:
    product_team: ProductTeam = data[create_product_team]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.write(entity=product_team)


def set_http_status(data, cache) -> tuple[HTTPStatus, dict]:
    product_team: ProductTeam = data[create_product_team]
    return HTTPStatus.CREATED, product_team.state()


steps = [
    parse_event_body,
    parse_incoming_product_team,
    validate_product_team_ods_code,
    create_product_team,
    save_product_team,
    set_http_status,
]
