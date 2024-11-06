from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from domain.response.response_models import SearchResponse
from event.step_chain import StepChain


def parse_incoming_path_parameters(data, cache) -> str:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return event.path_parameters["product_team_id"]


def validate_product_team(data, cache) -> str:
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    product_team_id = data[parse_incoming_path_parameters]
    return product_team_repo.read(id=product_team_id)


def query_products(data, cache) -> list:
    product_team_id = data[parse_incoming_path_parameters]
    cpm_product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = cpm_product_repo.query_products_by_product_team(
        product_team_id=product_team_id
    )
    return results


def return_products(data, cache) -> tuple[HTTPStatus, str]:
    products = data[query_products]
    response = SearchResponse(results=products)
    return HTTPStatus.OK, response.state()


steps = [
    parse_incoming_path_parameters,
    validate_product_team,
    query_products,
    return_products,
]
