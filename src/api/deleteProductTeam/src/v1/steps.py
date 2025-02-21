from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.enum import Status
from domain.core.error import ConflictError
from domain.core.product_team import ProductTeam
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.product_team_repository import ProductTeamRepository
from domain.request_models import ProductTeamPathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> ProductTeamPathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return ProductTeamPathParams(**event.path_parameters)


def read_product_team(data, cache) -> ProductTeam:
    path_params: ProductTeamPathParams = data[parse_path_params]
    product_team_repo: ProductTeamRepository = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.read(id=path_params.product_team_id)


def read_products(data, cache):
    product_team: ProductTeam = data[read_product_team]
    product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    cpm_products = product_repo.search_by_product_team(
        product_team_id=product_team.id, status=Status.ACTIVE
    )

    if cpm_products:
        product_ids = [str(product.id) for product in cpm_products]
        raise ConflictError(
            f"Product Team cannot be deleted as it still has associated Product Ids {product_ids}"
        )


def delete_product_team(data, cache) -> ProductTeamRepository:
    product_team: ProductTeam = data[read_product_team]
    product_team_repo: ProductTeamRepository = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    product_team.delete()
    return product_team_repo.write(product_team)


def set_http_status(data, cache) -> tuple[int, None]:
    product_team: ProductTeam = data[read_product_team]
    return HTTPStatus.OK, {
        "code": "RESOURCE_DELETED",
        "message": f"{product_team.id} has been deleted.",
    }


steps = [
    parse_path_params,
    read_product_team,
    read_products,
    delete_product_team,
    set_http_status,
]
