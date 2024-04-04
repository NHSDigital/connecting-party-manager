from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.device import DeviceType
from domain.repository.device_repository import DeviceRepository
from event.step_chain import StepChain

from ..data.response import devices, endpoints


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
    return DeviceType(device_query_param)


def read_devices_by_type(data, cache):
    device_type = data[set_device_type]
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.query_by_device_type(type=device_type)


def read_devices_by_id(data, cache):
    devices = data[read_devices_by_type]
    for device in devices:
        _read_devices_by_id(device)


def _read_devices_by_id(device):
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.read(device.get("pk1"))


def devices_to_fhir_bundle(data, cache) -> dict:
    devices = data[read_devices_by_id]
    return devices


# def device_to_fhir_org(data, cache) -> dict:
#     device = data[read_devices]
#     fhir_org = create_fhir_model_from_device(device=device)
#     return fhir_org.dict()


def get_results(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    device_type = event.query_string_parameters["device_type"]
    return {"product": devices, "endpoint": endpoints}.get(device_type.lower(), {})


steps = [
    parse_event_query,
    set_device_type,
    read_devices_by_type,
    read_devices_by_id,
    devices_to_fhir_bundle,
]
