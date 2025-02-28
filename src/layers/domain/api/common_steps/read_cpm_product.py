from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.cpm_product import CpmProduct
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.request_models import CpmProductReadPathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> CpmProductReadPathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return CpmProductReadPathParams(**event.path_parameters)


def read_product(data, cache) -> CpmProduct:
    path_params: CpmProductReadPathParams = data[parse_path_params]

    product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    cpm_product = product_repo.read(id=path_params.product_id)
    return cpm_product


def product_to_dict(data, cache) -> tuple[str, dict]:
    product: CpmProduct = data[read_product]
    return HTTPStatus.OK, product.state()


before_steps = [
    parse_path_params,
    read_product,
]
after_steps = [
    product_to_dict,
]
