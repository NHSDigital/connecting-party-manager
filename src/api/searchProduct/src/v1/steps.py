from http import HTTPStatus

from domain.core.error import ConfigurationError
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.response.response_models import SearchResponse
from event.step_chain import StepChain


def parse_incoming_query_parameters(data, cache) -> dict:
    query_params = data[StepChain.INIT].get("queryStringParameters", {})
    ## maybe refactor error here?
    # Check that at least one query parameter is provided
    if not query_params.get("organisation_code") and not query_params.get(
        "product_team_id"
    ):
        raise ConfigurationError(
            "At least one query parameter ('organisation_code' or 'product_team_id') must be provided."
        )

    # Ensure only one query parameter is provided
    if "organisation_code" in query_params and "product_team_id" in query_params:
        raise ConfigurationError(
            "Only one query parameter is allowed: 'organisation_code' or 'product_team_id'."
        )

    # Validate query parameters
    invalid_params = [
        key
        for key in query_params
        if key
        not in [
            "organisation_code",
            "product_team_id",
        ]  # put these in a variable somewhere
    ]
    if invalid_params:
        raise ConfigurationError(
            f"Invalid query parameter(s): {', '.join(invalid_params)}"
        )

    return query_params


def query_products(data, cache) -> list:
    query_params = data[parse_incoming_query_parameters]
    product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )

    if "product_team_id" in query_params:
        return product_repo.search_by_product_team(query_params["product_team_id"])
    elif "organisation_code" in query_params:
        return product_repo.search_by_organisation(query_params["organisation_code"])


def return_products(data, cache) -> tuple[HTTPStatus, str]:
    products = data[query_products]
    response = SearchResponse(results=products)
    return HTTPStatus.OK, response.state()


steps = [
    parse_incoming_query_parameters,
    query_products,
    return_products,
]
