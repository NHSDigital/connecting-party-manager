from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.cpm_product import CpmProduct
from domain.core.product_team import ProductTeam
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.product_team_repository import ProductTeamRepository
from domain.request_models import CpmProductPathParams
from domain.response.response_models import SearchResponse
from event.step_chain import StepChain


def parse_incoming_path_parameters(data, cache) -> CpmProductPathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return CpmProductPathParams(**event.path_parameters)


def read_product_team(data, cache) -> ProductTeam:
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    path_params: CpmProductPathParams = data[parse_incoming_path_parameters]
    return product_team_repo.read(id=path_params.product_team_id)


def read_product(data, cache) -> CpmProduct:
    cpm_product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    product_team: ProductTeam = data[read_product_team]
    path_params: CpmProductPathParams = data[parse_incoming_path_parameters]
    return cpm_product_repo.read(
        product_team_id=product_team.id, id=path_params.product_id
    )


def query_device_ref_data(data, cache) -> list[dict]:
    product_team: ProductTeam = data[read_product_team]
    product: CpmProduct = data[read_product]
    drd_repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = drd_repo.search(product_team_id=product_team.id, product_id=product.id)
    return results


def return_device_ref_data(data, cache) -> tuple[HTTPStatus, dict]:
    device_ref_data = data[query_device_ref_data]
    response = SearchResponse(results=device_ref_data)
    return HTTPStatus.OK, response.state()


steps = [
    parse_incoming_path_parameters,
    read_product_team,
    read_product,
    query_device_ref_data,
    return_device_ref_data,
]
