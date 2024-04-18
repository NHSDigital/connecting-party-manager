from typing import List

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.device import Device, DeviceType

# from domain.fhir_translation.device import create_fhir_model_from_devices
from domain.repository.device_repository import DeviceRepository
from event.step_chain import StepChain


# Think we require a validation decorator here.
def parse_event_query(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return (
        event.query_string_parameters["device_type"].upper()
        if event.query_string_parameters["device_type"]
        else None
    )


def set_device_type(data, cache):
    device_query_param = data[parse_event_query]
    return (
        DeviceType.PRODUCT if device_query_param == "PRODUCT" else DeviceType.ENDPOINT
    )


def read_devices_by_type(data, cache) -> List[Device]:
    device_type = data[set_device_type]
    print(device_type)  # noqa:T201
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.query_by_device_type(type=device_type)


# def read_devices_by_id(data, cache) -> List[Device]:
#     devices = data[read_devices_by_type]
#     print(devices)
#     full_devices = []
#     for device in devices:
#         full_devices.append(_read_devices_by_id(device))
#     return full_devices


# def _read_devices_by_id(device) -> Device:
#     device_repo = DeviceRepository(
#         table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
#     )
#     return device_repo.read(device.get("id"))


# def devices_to_fhir_bundle(data, cache) -> dict:
#     devices = data[read_devices_by_id]
#     print(devices)
#     fhir_org = create_fhir_model_from_devices(devices=devices)
#     return fhir_org.dict()


steps = [
    parse_event_query,
    set_device_type,
    read_devices_by_type,
    # read_devices_by_id,
    # devices_to_fhir_bundle,
]
