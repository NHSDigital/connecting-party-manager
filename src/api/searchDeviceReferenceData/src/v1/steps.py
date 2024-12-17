from http import HTTPStatus

from domain.api.common_steps.sub_product import (
    parse_path_params,
    read_environment,
    read_product,
    read_product_team,
)
from domain.core.cpm_product import CpmProduct
from domain.core.enum import Environment
from domain.core.product_team import ProductTeam
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.response.response_models import SearchResponse


def query_device_ref_data(data, cache) -> list[dict]:
    product_team: ProductTeam = data[read_product_team]
    product: CpmProduct = data[read_product]
    env: Environment = data[read_environment]
    drd_repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = drd_repo.search(
        product_team_id=product_team.id, product_id=product.id, environment=env
    )
    return results


def return_device_ref_data(data, cache) -> tuple[HTTPStatus, dict]:
    device_ref_data = data[query_device_ref_data]
    response = SearchResponse(results=device_ref_data)
    return HTTPStatus.OK, response.state()


steps = [
    parse_path_params,
    read_product_team,
    read_product,
    read_environment,
    query_device_ref_data,
    return_device_ref_data,
]
