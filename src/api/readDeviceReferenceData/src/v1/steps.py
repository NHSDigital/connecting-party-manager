from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.epr_product import EprProduct
from domain.core.product_team_epr import ProductTeam
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from domain.request_models import DeviceReferenceDataPathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> DeviceReferenceDataPathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return DeviceReferenceDataPathParams(**event.path_parameters)


def read_product_team(data, cache) -> ProductTeam:
    path_params: DeviceReferenceDataPathParams = data[parse_path_params]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return product_team_repo.read(id=path_params.product_team_id)


def read_product(data, cache) -> EprProduct:
    path_params: DeviceReferenceDataPathParams = data[parse_path_params]
    product_team: ProductTeam = data[read_product_team]

    product_repo = EprProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    epr_product = product_repo.read(
        product_team_id=product_team.id,
        id=path_params.product_id,
    )
    return epr_product


def read_device_reference_data(data, cache) -> DeviceReferenceData:
    path_params: DeviceReferenceDataPathParams = data[parse_path_params]
    product_team: ProductTeam = data[read_product_team]
    product: EprProduct = data[read_product]

    device_reference_data_repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_reference_data_repo.read(
        product_team_id=product_team.id,
        product_id=product.id,
        environment=path_params.environment,
        id=path_params.device_reference_data_id,
    )


def device_reference_data_to_dict(data, cache) -> tuple[str, dict]:
    device_reference_data: DeviceReferenceData = data[read_device_reference_data]
    return HTTPStatus.OK, device_reference_data.state()


steps = [
    parse_path_params,
    read_product_team,
    read_product,
    read_device_reference_data,
    device_reference_data_to_dict,
]
