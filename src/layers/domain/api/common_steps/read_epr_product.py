from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.epr_product import EprProduct
from domain.core.error import NotEprProductError
from domain.core.product_key import ProductKeyType
from domain.core.product_team_epr import ProductTeam
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from domain.request_models import CpmProductPathParams
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


def read_product(data, cache) -> EprProduct:
    path_params: CpmProductPathParams = data[parse_path_params]
    product_team: ProductTeam = data[read_product_team]

    product_repo = EprProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    epr_product = product_repo.read(
        product_team_id=product_team.id, id=path_params.product_id
    )
    return epr_product


def get_party_key(data, cache) -> str:
    product: EprProduct = data[read_product]
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


def product_to_dict(data, cache) -> tuple[str, dict]:
    product: EprProduct = data[read_product]
    return HTTPStatus.OK, product.state()


before_steps = [
    parse_path_params,
    read_product_team,
    read_product,
]
epr_product_specific_steps = [get_party_key]
after_steps = [
    product_to_dict,
]
