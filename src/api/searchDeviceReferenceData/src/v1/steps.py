from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from domain.request_models.v1 import CpmProductPathParams
from domain.response.response_models import SearchResponse
from event.step_chain import StepChain


def parse_incoming_path_parameters(data, cache) -> str:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return CpmProductPathParams(**event.path_parameters)


def validate_product_team(data, cache) -> str:
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    path_params = data[parse_incoming_path_parameters]
    return product_team_repo.read(id=path_params["product_team_id"])


def validate_product(data, cache) -> str:
    cpm_product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    path_params = data[parse_incoming_path_parameters]
    return cpm_product_repo.read(id=path_params["product_id"])


def query_device_ref_data(data, cache) -> list:
    product_team = data[validate_product_team]
    product = data[validate_product]
    drd_repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = drd_repo.search(product_team_id=product_team.id, product_id=product.id)
    return results


def return_device_ref_data(data, cache) -> tuple[HTTPStatus, str]:
    device_ref_data = data[query_device_ref_data]
    response = SearchResponse(results=device_ref_data)
    return HTTPStatus.OK, response.state()


steps = [
    parse_incoming_path_parameters,
    validate_product_team,
    validate_product,
    query_device_ref_data,
    return_device_ref_data,
]
