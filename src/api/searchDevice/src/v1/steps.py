from typing import List

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.device import Device, DeviceType
from domain.fhir_translation.device import create_fhir_searchset_bundle
from domain.repository.device_repository import DeviceRepository
from domain.repository.marshall import unmarshall_value
from event.step_chain import StepChain


# Think we require a validation decorator here.
def parse_event_query(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return (
        {
            "query_string": event.query_string_parameters["device_type"].upper(),
            "host": event.multi_value_headers["Host"],
        }
        if event.query_string_parameters["device_type"]
        else None
    )


def set_device_type(data, cache):
    event_data = data[parse_event_query]
    device_query_param = event_data.get("query_string")
    return (
        DeviceType.PRODUCT if device_query_param == "PRODUCT" else DeviceType.ENDPOINT
    )


def read_devices_by_type(data, cache) -> List[Device]:
    device_type = data[set_device_type]
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.query_by_device_type(type=device_type)


def read_devices_by_id(data, cache) -> List[Device]:
    devices = data[read_devices_by_type]
    full_devices = []
    for device in devices.get("Items"):
        full_devices.append(
            _read_devices_by_id(
                device,
                table_name=cache["DYNAMODB_TABLE"],
                dynamodb_client=cache["DYNAMODB_CLIENT"],
            )
        )
    return full_devices


def _read_devices_by_id(device, table_name, dynamodb_client) -> Device:
    device_id = device.get("id")
    device_id = unmarshall_value(device_id)
    device_repo = DeviceRepository(
        table_name=table_name, dynamodb_client=dynamodb_client
    )
    return device_repo.read(id=device_id)


def devices_to_fhir_bundle(data, cache) -> dict:
    event_data = data[parse_event_query]
    device_type = event_data.get("query_string")
    host = event_data.get("host")[0]
    devices = data[read_devices_by_id]
    fhir_org = create_fhir_searchset_bundle(
        devices=devices, device_type=device_type, host=host
    )
    return fhir_org.dict()


steps = [
    parse_event_query,
    set_device_type,
    read_devices_by_type,
    read_devices_by_id,
    devices_to_fhir_bundle,
]
