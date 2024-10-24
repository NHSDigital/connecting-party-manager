from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.product_team.v3 import ProductTeam
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from domain.request_models.v1 import CpmProductPathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> CpmProductPathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return CpmProductPathParams(**event.path_parameters)


def read_product_team(data, cache) -> ProductTeam:
    path_params: CpmProductPathParams = data[parse_path_params]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.read(id=path_params.product_team_id)


def read_product(data, cache) -> CpmProduct:
    path_params: CpmProductPathParams = data[parse_path_params]
    product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    cpm_product = product_repo.read(
        product_id=path_params.product_id, product_team_id=path_params.product_team_id
    )
    return cpm_product


def product_to_dict(data, cache) -> dict:
    product: CpmProduct = data[read_product]
    return product.state()


before_steps = [
    parse_path_params,
    read_product_team,
    read_product,
]
after_steps = [
    product_to_dict,
]
