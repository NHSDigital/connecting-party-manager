from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.cpm_product import CpmProduct
from domain.core.cpm_system_id import ProductId
from domain.core.product_team.v3 import ProductTeam
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from domain.request_models.v1 import (
    CreateCpmProductIncomingParams,
    ProductTeamPathParams,
)
from domain.response.validation_errors import (
    InboundValidationError,
    mark_json_decode_errors_as_inbound,
    mark_validation_errors_as_inbound,
)
from event.step_chain import StepChain
from pydantic import ValidationError


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> ProductTeamPathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return ProductTeamPathParams(**event.path_parameters)


@mark_json_decode_errors_as_inbound
def parse_event_body(data, cache) -> dict:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return event.json_body if event.body else {}


def parse_incoming_cpm_product(data, cache) -> CreateCpmProductIncomingParams:
    json_body = data[parse_event_body]
    try:
        incoming_product = CreateCpmProductIncomingParams(**json_body)
        return incoming_product
    except ValidationError as exc:
        raise InboundValidationError(errors=exc.raw_errors, model=exc.model)


def read_product_team(data, cache) -> ProductTeam:
    path_params: ProductTeamPathParams = data[parse_path_params]

    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.read(id=path_params.product_team_id)


def generate_cpm_product_id(data, cache) -> str:
    generated_product_id = ProductId.create()
    return generated_product_id.id


@mark_validation_errors_as_inbound
def create_cpm_product(data, cache) -> CpmProduct:
    incoming_product = data[parse_incoming_cpm_product]
    product_team: ProductTeam = data[read_product_team]
    product_id = data[generate_cpm_product_id]
    product = product_team.create_cpm_product(
        product_id=product_id, name=incoming_product.product_name
    )
    return product


def save_cpm_product(data, cache) -> dict:
    cpm_product = data[create_cpm_product]
    cpm_product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return cpm_product_repo.write(entity=cpm_product)


def set_http_status(data, cache) -> tuple[HTTPStatus, str]:
    product: CpmProduct = data[create_cpm_product]
    return HTTPStatus.CREATED, str(product.id)


steps = [
    parse_path_params,
    parse_event_body,
    parse_incoming_cpm_product,
    read_product_team,
    generate_cpm_product_id,
    create_cpm_product,
    save_cpm_product,
    set_http_status,
]
