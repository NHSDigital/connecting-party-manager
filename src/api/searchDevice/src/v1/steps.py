from typing import List

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.api.query import SearchQueryParams
from domain.core.device import Device
from domain.fhir_translation.device import create_fhir_searchset_bundle
from domain.repository.device_repository import DeviceRepository
from domain.repository.marshall import unmarshall_value
from domain.response.validation_errors import InboundValidationError
from event.step_chain import StepChain
from pydantic import ValidationError

from ..data.response_v2 import devices, endpoints


def get_mocked_results(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    query_params = event.query_string_parameters
    search_query_params = SearchQueryParams(**query_params)
    params = search_query_params.get_non_null_params()
    device_type = params["device_type"]
    return {"product": devices, "endpoint": endpoints}.get(device_type.lower(), {})


def parse_event_query(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    query_params = event.query_string_parameters
    try:
        search_query_params = SearchQueryParams(**query_params)
        params = search_query_params.get_non_null_params()
        return {
            "query_string": params,
            "host": event.multi_value_headers["Host"],
        }
    except ValidationError as exc:
        raise InboundValidationError(
            errors=exc.raw_errors,
            model=exc.model,
        )


def query_devices(data, cache) -> List[Device]:
    pass


def read_devices_by_type(data, cache) -> List[Device]:
    event_data = data[parse_event_query]
    query_params = event_data.get("query_string")
    device_type = query_params.get("device_type")
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.query_by_device_type(type=device_type)


def read_devices_by_id(data, cache) -> List[Device]:
    devices = data[read_devices_by_type]
    full_devices = []
    for device in devices.get("Items"):
        if unmarshall_value(device.get("status", {"S": "inactive"})) == "active":
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
    read_devices_by_type,
    read_devices_by_id,
    devices_to_fhir_bundle,
]

mocked_steps = [
    get_mocked_results,
]
