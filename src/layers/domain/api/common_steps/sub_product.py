from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.cpm_product import CpmProduct
from domain.core.enum import Environment
from domain.core.error import NotEprProductError
from domain.core.product_key import ProductKeyType
from domain.core.product_team_epr import ProductTeam
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from domain.request_models import CpmProductPathParams, SubCpmProductPathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> SubCpmProductPathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return SubCpmProductPathParams(**event.path_parameters)


def read_product_team(data, cache) -> ProductTeam:
    path_params: CpmProductPathParams = data[parse_path_params]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.read(id=path_params.product_team_id)


def read_product(data, cache) -> CpmProduct:
    path_params: CpmProductPathParams = data[parse_path_params]
    product_team: ProductTeam = data[read_product_team]

    product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    cpm_product = product_repo.read(
        product_team_id=product_team.id, id=path_params.product_id
    )
    return cpm_product


def read_environment(data, cache) -> Environment:
    path_params: SubCpmProductPathParams = data[parse_path_params]
    return path_params.environment


def get_party_key(data, cache) -> str:
    product: CpmProduct = data[read_product]
    party_keys = (
        key.key_value
        for key in product.keys
        if key.key_type is ProductKeyType.PARTY_KEY
    )
    try:
        (party_key,) = party_keys
    except ValueError:
        raise NotEprProductError(
            "Not an EPR Product: Cannot create MHS Device for product without exactly one Party Key"
        )
    return party_key
