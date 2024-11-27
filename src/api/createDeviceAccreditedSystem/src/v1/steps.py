from http import HTTPStatus

from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.read_product import (
    parse_path_params,
    read_product,
    read_product_team,
)
from domain.core.cpm_product import CpmProduct
from domain.core.device import (
    Device,
    DeviceTagAddedEvent,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.error import (
    AccreditedSystemFatalError,
    ConfigurationError,
    NotEprProductError,
)
from domain.core.product_key import ProductKeyType
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository import DeviceRepository
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from domain.request_models import CpmProductPathParams, CreateAsDeviceIncomingParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from sds.epr.constants import EprNameTemplate


@mark_validation_errors_as_inbound
def parse_as_device_payload(data, cache) -> CreateAsDeviceIncomingParams:
    payload: dict = data[parse_event_body]
    return CreateAsDeviceIncomingParams(**payload)


def read_device_reference_data(data, cache) -> list[DeviceReferenceData]:
    path_params: CpmProductPathParams = data[parse_path_params]
    product_repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    device_reference_data = product_repo.search(
        product_id=path_params.product_id,
        product_team_id=path_params.product_team_id,
    )

    # Only 1 AS DRD and only 1 MHS DRD

    if not device_reference_data or len(device_reference_data) < 2:
        raise ConfigurationError(
            "You must configure the AS and MessageSet Device Reference Data before creating an AS Device"
        )

    if len(device_reference_data) > 2:
        raise AccreditedSystemFatalError(
            "More that 2 MessageSet Device Reference Data resources were found. This is not allowed"
        )

    exists = set()
    if any(drd.name in exists or exists.add(drd.name) for drd in device_reference_data):
        raise ConfigurationError(
            "Only one AS and one MessageSet Device Reference Data is allowed before creating an AS Device"
        )

    return device_reference_data


def read_spine_as_questionnaire(data, cache) -> Questionnaire:
    return QuestionnaireRepository().read(QuestionnaireInstance.SPINE_AS)


def validate_spine_as_questionnaire_response(data, cache) -> QuestionnaireResponse:
    spine_as_questionnaire: Questionnaire = data[read_spine_as_questionnaire]
    payload: CreateAsDeviceIncomingParams = data[parse_as_device_payload]
    spine_as_questionnaire_response = payload.questionnaire_responses[
        QuestionnaireInstance.SPINE_AS
    ]
    return spine_as_questionnaire.validate(
        data=spine_as_questionnaire_response.__root__[0]
    )


def create_as_device(data, cache) -> Device:
    product: CpmProduct = data[read_product]
    payload: CreateAsDeviceIncomingParams = data[parse_as_device_payload]
    party_key: str = data[get_party_key]

    # Create a new Device dictionary excluding 'questionnaire_responses'
    # Ticket PI-666 adds ASID generation. This will need to be sent across in the arguments instead of an empty string.
    device_payload = payload.dict(exclude={"questionnaire_responses"})
    return product.create_device(
        name=EprNameTemplate.AS_DEVICE.format(party_key=party_key, asid=""),
        **device_payload
    )


def create_party_key_tag(data, cache) -> DeviceTagAddedEvent:
    as_device: Device = data[create_as_device]
    return as_device.add_tag(party_key=data[get_party_key])


def create_device_keys(data, cache) -> Device:
    # We will need to add some keys in the future, ASID?
    as_device: Device = data[create_as_device]
    return as_device


def add_device_reference_data_id(data, cache) -> Device:
    as_device: Device = data[create_device_keys]
    device_reference_data: DeviceReferenceData = data[read_device_reference_data]
    for drd in device_reference_data:
        as_device.add_device_reference_data_id(
            device_reference_data_id=str(drd.id), path_to_data=["Interaction ID"]
        )
    return as_device


def add_spine_as_questionnaire_response(
    data, cache
) -> QuestionnaireResponseUpdatedEvent:
    spine_as_questionnaire_response: QuestionnaireResponse = data[
        validate_spine_as_questionnaire_response
    ]
    as_device: Device = data[create_as_device]

    return as_device.add_questionnaire_response(spine_as_questionnaire_response)


def write_device(data: dict[str, Device], cache) -> Device:
    as_device: Device = data[create_as_device]
    repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return repo.write(as_device)


def set_http_status(data, cache) -> tuple[HTTPStatus, dict]:
    as_device: Device = data[create_as_device]
    return HTTPStatus.CREATED, as_device.state_exclude_tags()


def get_party_key(data, cache) -> str:
    product: CpmProduct = data[read_product]
    party_keys = (
        key.key_value
        for key in product.keys
        if key.key_type is ProductKeyType.PARTY_KEY
    )
    try:
        (party_key,) = party_keys
    except ValueError:
        raise NotEprProductError(
            "Not an EPR Product: Cannot create AS device for product without exactly one Party Key"
        )
    return party_key


steps = [
    parse_event_body,
    parse_path_params,
    parse_as_device_payload,
    read_product_team,
    read_product,
    get_party_key,
    read_device_reference_data,
    read_spine_as_questionnaire,
    validate_spine_as_questionnaire_response,
    create_as_device,
    create_party_key_tag,
    create_device_keys,
    add_device_reference_data_id,
    add_spine_as_questionnaire_response,
    write_device,
    set_http_status,
]
