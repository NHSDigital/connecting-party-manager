from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v3 import Device
from domain.core.product_team.v3 import ProductTeam
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.device_repository.v3 import DeviceRepository
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from domain.request_models.v1 import DevicePathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> DevicePathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return DevicePathParams(**event.path_parameters)


def read_product_team(data, cache) -> ProductTeam:
    path_params: DevicePathParams = data[parse_path_params]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.read(id=path_params.product_team_id)


def read_product(data, cache) -> CpmProduct:
    path_params: DevicePathParams = data[parse_path_params]
    product_team: ProductTeam = data[read_product_team]

    product_repo = CpmProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    cpm_product = product_repo.read(
        id=path_params.product_id, product_team_id=product_team.id
    )
    return cpm_product


def read_device(data, cache) -> Device:
    path_params: DevicePathParams = data[parse_path_params]
    product_team: ProductTeam = data[read_product_team]
    product: CpmProduct = data[read_product]

    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.read(
        product_team_id=product_team.id,
        product_id=product.id,
        id=path_params.device_id,
    )


def device_to_dict(data, cache) -> tuple[str, dict]:
    device: Device = data[read_device]
    return HTTPStatus.OK, device.state()


steps = [
    parse_path_params,
    read_product_team,
    read_product,
    read_device,
    device_to_dict,
]
