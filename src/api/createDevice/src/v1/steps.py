from http import HTTPStatus

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from domain.core.device import Device
from domain.core.device_id import generate_device_key
from domain.core.device_key import DeviceKeyType
from domain.core.product_team.v1 import ProductTeam
from domain.fhir.r4.cpm_model import SYSTEM
from domain.fhir.r4.cpm_model import Device as FhirDevice
from domain.fhir_translation.device import (
    create_domain_device_from_fhir_device,
    parse_fhir_device_json,
)
from domain.repository.device_repository import DeviceRepository
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from domain.response.validation_errors import mark_json_decode_errors_as_inbound
from event.aws.client import dynamodb_client
from event.step_chain import StepChain


@mark_json_decode_errors_as_inbound
def parse_event_body(data, cache) -> dict:
    event = APIGatewayProxyEvent(data[StepChain.INIT])
    return event.json_body if event.body else {}


def parse_fhir_device(data, cache) -> FhirDevice:
    json_body = data[parse_event_body]
    identifier = json_body.get("identifier", [])
    identifier.append(
        dict(
            system=f"{SYSTEM}/{DeviceKeyType.PRODUCT_ID}",
            value=generate_device_key(DeviceKeyType.PRODUCT_ID),
        )
    )
    json_body["identifier"] = identifier
    fhir_device = parse_fhir_device_json(fhir_device_json=json_body)
    return fhir_device


def read_product_team(data, cache) -> ProductTeam:
    fhir_device: FhirDevice = data[parse_fhir_device]
    product_team_repo = ProductTeamRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=dynamodb_client()
    )
    return product_team_repo.read(id=fhir_device.owner.identifier.value)


def create_device(data, cache) -> Device:
    fhir_device: FhirDevice = data[parse_fhir_device]
    product_team: ProductTeam = data[read_product_team]
    device = create_domain_device_from_fhir_device(
        fhir_device=fhir_device, product_team=product_team
    )
    return device


def save_device(data, cache) -> dict:
    device = data[create_device]
    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return device_repo.write(entity=device)


def set_http_status(data, cache) -> tuple[HTTPStatus, str]:
    device: Device = data[create_device]
    return HTTPStatus.CREATED, str(device.id)


steps = [
    parse_event_body,
    parse_fhir_device,
    read_product_team,
    create_device,
    save_device,
    set_http_status,
]
