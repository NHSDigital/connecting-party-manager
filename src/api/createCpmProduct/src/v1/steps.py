from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.cpm_product import CpmProduct, CpmProductIncomingParams
from domain.core.product_team.v3 import ProductTeam
from domain.repository.product_team_repository import ProductTeamRepository
from domain.response.validation_errors import (
    InboundValidationError,
    mark_json_decode_errors_as_inbound,
)
from event.aws.client import dynamodb_client
from event.step_chain import StepChain
from pydantic import ValidationError


@mark_json_decode_errors_as_inbound
def parse_event_body(data, cache) -> dict:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return event.json_body if event.body else {}


def parse_incoming_cpm_product(data, cache) -> CpmProductIncomingParams:
    json_body = data[parse_event_body]
    try:
        incoming_product = CpmProductIncomingParams(**json_body)
        return incoming_product
    except ValidationError as exc:
        raise InboundValidationError(errors=exc.raw_errors, model=exc.model)


def read_product_team(data, cache) -> ProductTeam:
    incoming_product = data[parse_incoming_cpm_product]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=dynamodb_client()
    )
    return product_team_repo.read(id=incoming_product.product_team_id)


def generate_cpm_product_id(data, cache) -> str:
    return "P.123-456"


def create_cpm_product(data, cache) -> CpmProduct:
    incoming_product = data[parse_incoming_cpm_product]
    product_team: ProductTeam = data[read_product_team]
    product_id = data[generate_cpm_product_id]
    product = product_team.create_cpm_product(
        product_id=product_id, name=incoming_product.product_name
    )
    return product


def set_http_status(data, cache) -> tuple[HTTPStatus, str]:
    product: Product = data[create_cpm_product]
    return HTTPStatus.CREATED, str(product.id)


steps = [
    parse_event_body,
    parse_incoming_cpm_product,
    read_product_team,
    generate_cpm_product_id,
    create_cpm_product,
    # save_product_team,
    set_http_status,
]
