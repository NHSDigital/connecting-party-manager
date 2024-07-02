from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.device import Device
from domain.fhir_translation.device import create_fhir_model_from_device
from domain.repository.device_repository import DeviceRepository
from event.step_chain import StepChain


def read_device(data, cache) -> Device:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    device_id = event.path_parameters["id"]
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.read_by_id(id=device_id)


def device_to_fhir_org(data, cache) -> dict:
    device = data[read_device]
    fhir_org = create_fhir_model_from_device(device=device)
    return fhir_org.dict()


steps = [
    read_device,
    device_to_fhir_org,
]
