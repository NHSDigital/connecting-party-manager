from http import HTTPStatus

from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.sub_product import (
    parse_path_params,
    read_environment,
    read_product,
    read_product_team,
)
from domain.core.device import Device
from domain.core.epr_product import EprProduct
from domain.repository.device_repository import DeviceRepository
from domain.request_models import CreateDeviceIncomingParams
from domain.response.validation_errors import mark_validation_errors_as_inbound


@mark_validation_errors_as_inbound
def parse_device_payload(data, cache) -> CreateDeviceIncomingParams:
    payload: dict = data[parse_event_body]
    return CreateDeviceIncomingParams(**payload)


def create_device(data, cache) -> Device:
    product: EprProduct = data[read_product]
    payload: CreateDeviceIncomingParams = data[parse_device_payload]
    environment = data[read_environment]
    return product.create_device(environment=environment, **payload.dict())


def write_device(data: dict[str, EprProduct], cache) -> EprProduct:
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
    read_environment,
    parse_device_payload,
    read_product_team,
    read_product,
    create_device,
    write_device,
    set_http_status,
]
