from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.product_team.v3 import ProductTeam
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from domain.request_models.v1 import ProductTeamPathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> ProductTeamPathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return ProductTeamPathParams(**event.path_parameters)


def read_product_team(data, cache) -> ProductTeam:
    path_params: ProductTeamPathParams = data[parse_path_params]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.read(id=path_params.product_team_id)


def return_product_team(data, cache) -> tuple[HTTPStatus, dict]:
    product_team: ProductTeam = data[read_product_team]
    return HTTPStatus.OK, product_team.state()


steps = [parse_path_params, read_product_team, return_product_team]
