from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.enum import Status
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.errors import ItemNotFound
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from domain.request_models.v1 import SearchProductQueryParams
from domain.response.response_models import SearchProductResponse
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def _parse_event_query(query_params: dict):
    search_query_params = SearchProductQueryParams(**query_params)
    return search_query_params.get_non_null_params()


def parse_event_query(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    query_params = _parse_event_query(query_params=event.query_string_parameters or {})
    return {
        "query_params": query_params,
        "host": event.multi_value_headers["Host"],
    }


def query_products(data, cache) -> list:
    event_data: dict = data[parse_event_query]
    query_params: dict = event_data.get("query_params")
    product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )

    if "product_team_id" in query_params:
        product_team_repo = ProductTeamRepository(
            table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
        )
        # Allow product team id or product team alias
        try:
            product_team = product_team_repo.read(id=query_params["product_team_id"])
        except ItemNotFound:
            return []
        product_team_id = product_team.id
        return product_repo.search_by_product_team(
            product_team_id, status=Status.ACTIVE
        )
    elif "organisation_code" in query_params:
        return product_repo.search_by_organisation(
            query_params["organisation_code"], status=Status.ACTIVE
        )


def return_products(data, cache) -> tuple[HTTPStatus, str]:
    cpm_products = data[query_products]
    response = SearchProductResponse(cpm_products)

    return HTTPStatus.OK, response.state()


steps = [
    parse_event_query,
    query_products,
    return_products,
]
