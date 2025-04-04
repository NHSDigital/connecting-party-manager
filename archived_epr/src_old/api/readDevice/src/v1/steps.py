from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.device import Device
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.epr_product import EprProduct
from domain.core.product_team_epr import ProductTeam
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository import DeviceRepository
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from domain.request_models import DevicePathParams
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


def read_product(data, cache) -> EprProduct:
    path_params: DevicePathParams = data[parse_path_params]
    product_team: ProductTeam = data[read_product_team]

    product_repo = EprProductRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    epr_product = product_repo.read(
        id=path_params.product_id, product_team_id=product_team.id
    )
    return epr_product


def read_device(data, cache) -> Device:
    path_params: DevicePathParams = data[parse_path_params]
    product_team: ProductTeam = data[read_product_team]
    product: EprProduct = data[read_product]

    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.read(
        product_team_id=product_team.id,
        product_id=product.id,
        environment=path_params.environment,
        id=path_params.device_id,
    )


def read_device_reference_data(data, cache) -> list[DeviceReferenceData]:
    path_params: DevicePathParams = data[parse_path_params]
    product_team: ProductTeam = data[read_product_team]
    product: EprProduct = data[read_product]
    device: Device = data[read_device]

    device_reference_datas = []
    device_reference_data_repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    for id in device.device_reference_data:
        drd = device_reference_data_repo.read(
            product_team_id=product_team.id,
            product_id=product.id,
            environment=path_params.environment,
            id=id,
        )
        device_reference_datas.append(drd)
    return device_reference_datas


def filter_by_jsonpath(data, filters: list) -> dict:
    response = {}
    if "*" not in filters:
        response = {
            filter_key.lstrip("*."): data[filter_key.lstrip("*.")]
            for filter_key in filters
        }
        return response
    return data


def filter_device_reference_data(data, cache) -> list[DeviceReferenceData]:
    device: Device = data[read_device]
    device_reference_data_list: list[DeviceReferenceData] = data[
        read_device_reference_data
    ]

    for drd in device_reference_data_list:
        filters = device.device_reference_data[str(drd.id)]
        for questionnaire_response in drd.questionnaire_responses.values():
            for qr in questionnaire_response:
                qr.data = filter_by_jsonpath(data=qr.data, filters=filters)
    return device_reference_data_list


def update_device_with_device_reference_data(data, cache) -> Device:
    device: Device = data[read_device]
    device_reference_datas = data[read_device_reference_data]
    [
        device.questionnaire_responses.setdefault(key, []).extend(responses)
        for drd in device_reference_datas
        for key, responses in drd.questionnaire_responses.items()
    ]

    return device


def device_to_dict(data, cache) -> tuple[str, dict]:
    device: Device = data[read_device]
    return HTTPStatus.OK, device.state()


steps = [
    parse_path_params,
    read_product_team,
    read_product,
    read_device,
    read_device_reference_data,
    filter_device_reference_data,
    update_device_with_device_reference_data,
    device_to_dict,
]
