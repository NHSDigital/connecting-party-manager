from http import HTTPStatus
from typing import TYPE_CHECKING

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.api.common_steps.general import parse_event_body
from domain.core.epr_product import EprProduct
from domain.core.product_team_epr import ProductTeam
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from domain.request_models import CreateCpmProductIncomingParams, ProductTeamPathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.type_defs import TransactWriteItemsOutputTypeDef


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> ProductTeamPathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return ProductTeamPathParams(**event.path_parameters)


@mark_validation_errors_as_inbound
def parse_incoming_epr_product(data, cache) -> CreateCpmProductIncomingParams:
    json_body = data[parse_event_body]
    incoming_product = CreateCpmProductIncomingParams(**json_body)
    return incoming_product


def read_product_team(data, cache) -> ProductTeam:
    path_params: ProductTeamPathParams = data[parse_path_params]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.read(id=path_params.product_team_id)


def create_epr_product(
    data: dict[str, CreateCpmProductIncomingParams | ProductTeam], cache
) -> EprProduct:
    incoming_product: CreateCpmProductIncomingParams = data[parse_incoming_epr_product]
    product_team: ProductTeam = data[read_product_team]
    product = product_team.create_epr_product(name=incoming_product.name)
    return product


def write_epr_product(
    data: dict[str, EprProduct], cache
) -> list["TransactWriteItemsOutputTypeDef"]:
    product: EprProduct = data[create_epr_product]
    product_repo = EprProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_repo.write(product)


def set_http_status(data, cache) -> tuple[HTTPStatus, EprProduct]:
    product: EprProduct = data[create_epr_product]
    return HTTPStatus.CREATED, product.state()


before_steps = [
    parse_path_params,
    parse_event_body,
    parse_incoming_epr_product,
    read_product_team,
    create_epr_product,
]

after_steps = [
    write_epr_product,
    set_http_status,
]
