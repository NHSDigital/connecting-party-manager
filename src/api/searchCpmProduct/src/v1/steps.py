from http import HTTPStatus
from typing import List

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.cpm_product import CpmProduct
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.product_team_repository.v2 import ProductTeamRepository
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


def query_products(data, cache) -> List[CpmProduct]:
    product_team_id = data[parse_incoming_path_parameters]
    cpm_product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = cpm_product_repo.query_products_by_product_team(
        product_team_id=product_team_id
    )
    return HTTPStatus.OK, [result.state() for result in results]


steps = [
    parse_incoming_path_parameters,
    validate_product_team,
    query_products,
]
