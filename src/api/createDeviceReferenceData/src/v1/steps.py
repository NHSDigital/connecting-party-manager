from http import HTTPStatus

from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.sub_product import (
    parse_path_params,
    read_environment,
    read_product,
    read_product_team,
)
from domain.core.cpm_product import CpmProduct
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.enum import Environment
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.request_models import CreateDeviceReferenceDataIncomingParams
from domain.response.validation_errors import mark_validation_errors_as_inbound


@mark_validation_errors_as_inbound
def parse_device_reference_data_payload(
    data, cache
) -> CreateDeviceReferenceDataIncomingParams:
    payload: dict = data[parse_event_body]
    return CreateDeviceReferenceDataIncomingParams(**payload)


def create_device_reference_data(data, cache) -> DeviceReferenceData:
    product: CpmProduct = data[read_product]
    payload: CreateDeviceReferenceDataIncomingParams = data[
        parse_device_reference_data_payload
    ]
    environment: Environment = data[read_environment]
    return product.create_device_reference_data(
        environment=environment, **payload.dict()
    )


def write_device_reference_data(data: dict[str, CpmProduct], cache) -> CpmProduct:
    device_reference_data: DeviceReferenceData = data[create_device_reference_data]
    repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return repo.write(device_reference_data)


def set_http_status(data, cache) -> tuple[HTTPStatus, str]:
    device_reference_data: DeviceReferenceData = data[create_device_reference_data]
    return HTTPStatus.CREATED, device_reference_data.state()


steps = [
    parse_event_body,
    parse_path_params,
    read_environment,
    parse_device_reference_data_payload,
    read_product_team,
    read_product,
    create_device_reference_data,
    write_device_reference_data,
    set_http_status,
]
