from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.fhir_translation.device import create_fhir_model_from_device
from domain.repository.device_repository import DeviceRepository
from event.step_chain import StepChain

from ..data.response import devices, endpoints


def read_devices(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    device_type = event.query_string_parameters["device_type"]
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.query_by_device_type(type=device_type)


def device_to_fhir_org(data, cache) -> dict:
    device = data[read_devices]
    fhir_org = create_fhir_model_from_device(device=device)
    return fhir_org.dict()


def get_results(data, cache):
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    device_type = event.query_string_parameters["device_type"]
    return {"product": devices, "endpoint": endpoints}.get(device_type.lower(), {})


steps = [
    get_results,
]
