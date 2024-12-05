from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.read_product import read_product, read_product_team
from domain.core.cpm_product import CpmProduct
from domain.core.device import Device
from domain.repository.device_repository import DeviceRepository
from domain.request_models import CreateDeviceIncomingParams, CreateDevicePathParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain


@mark_validation_errors_as_inbound
def parse_device_payload(data, cache) -> CreateDeviceIncomingParams:
    payload: dict = data[parse_event_body]
    return CreateDeviceIncomingParams(**payload)


@mark_validation_errors_as_inbound
def parse_path_params(data, cache) -> CreateDevicePathParams:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return CreateDevicePathParams(**event.path_parameters)


def create_device(data, cache) -> Device:
    product: CpmProduct = data[read_product]
    payload: CreateDeviceIncomingParams = data[parse_device_payload]
    return product.create_device(**payload.dict())


def write_device(data: dict[str, CpmProduct], cache) -> CpmProduct:
    device: Device = data[create_device]
    repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return repo.write(device)


def set_http_status(data, cache) -> tuple[HTTPStatus, str]:
    device: Device = data[create_device]
    return HTTPStatus.CREATED, device.state()


steps = [
    parse_event_body,
    parse_path_params,
    parse_device_payload,
    read_product_team,
    read_product,
    create_device,
    write_device,
    set_http_status,
]
