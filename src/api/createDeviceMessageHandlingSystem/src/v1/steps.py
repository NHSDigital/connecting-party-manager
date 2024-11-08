from http import HTTPStatus

from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.read_product import (
    parse_path_params,
    read_product,
    read_product_team,
)
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v3 import Device
from domain.core.error import InvalidSpineMhsResponse, NotEprProductError
from domain.core.product_key.v1 import ProductKeyType
from domain.core.questionnaire.v3 import Questionnaire, QuestionnaireResponse
from domain.repository.device_repository.v3 import DeviceRepository
from domain.repository.questionnaire_repository.v2 import QuestionnaireRepository
from domain.repository.questionnaire_repository.v2.questionnaires import (
    QuestionnaireInstance,
)
from domain.request_models.v1 import CreateMhsDeviceIncomingParams
from domain.response.validation_errors import mark_validation_errors_as_inbound


@mark_validation_errors_as_inbound
def parse_mhs_device_payload(data, cache) -> Device:
    payload: dict = data[parse_event_body]
    return CreateMhsDeviceIncomingParams(**payload)


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
            "Not an EPR Product: Cannot create MHS device for product without exactly one Party Key"
        )
    return party_key


def read_spine_mhs_questionnaire(data, cache) -> Questionnaire:
    return QuestionnaireRepository().read(QuestionnaireInstance.SPINE_MHS)


def validate_spine_mhs_questionnaire_response(data, cache) -> QuestionnaireResponse:
    spine_mhs_questionnaire: Questionnaire = data[read_spine_mhs_questionnaire]
    payload: CreateMhsDeviceIncomingParams = data[parse_mhs_device_payload]
    questionnaire_responses = payload.questionnaire_responses

    # Ensure there's a questionnaire named 'spine_mhs' in the responses
    if QuestionnaireInstance.SPINE_MHS not in questionnaire_responses:
        raise InvalidSpineMhsResponse(
            "Require a 'spine_mhs' questionnaire response to create a MHS Device"
        )

    raw_spine_mhs_questionnaire_response = payload.questionnaire_responses[
        QuestionnaireInstance.SPINE_MHS
    ]
    # Ensure there's only one response to 'spine_mhs'
    if len(raw_spine_mhs_questionnaire_response) != 1:
        raise InvalidSpineMhsResponse(
            "Expected only one response for the 'spine_mhs' questionnaire"
        )

    return spine_mhs_questionnaire.validate(
        data=raw_spine_mhs_questionnaire_response[0]
    )


def create_mhs_device(data, cache) -> Device:
    product: CpmProduct = data[read_product]
    payload: CreateMhsDeviceIncomingParams = data[parse_mhs_device_payload]

    # Create a new Device dictionary excluding 'questionnaire_responses'
    device_payload = payload.dict(exclude={"questionnaire_responses"})
    return product.create_device(**device_payload)


def create_party_key_tag(data, cache):
    mhs_device: Device = data[create_mhs_device]
    mhs_device.add_tag(party_key=data[get_party_key])
    return mhs_device


def add_spine_mhs_questionnaire_response(data, cache) -> list[QuestionnaireResponse]:
    spine_mhs_questionnaire_response: QuestionnaireResponse = data[
        validate_spine_mhs_questionnaire_response
    ]
    mhs_device: Device = data[create_party_key_tag]
    mhs_device.add_questionnaire_response(spine_mhs_questionnaire_response)
    return mhs_device


def write_device(data: dict[str, CpmProduct], cache) -> CpmProduct:
    mhs_device: Device = data[add_spine_mhs_questionnaire_response]
    repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return repo.write(mhs_device)


def set_http_status(data, cache) -> tuple[HTTPStatus, str]:
    device: Device = data[create_mhs_device]
    return HTTPStatus.CREATED, device.state_exclude_tags()


steps = [
    parse_event_body,
    parse_path_params,
    parse_mhs_device_payload,
    read_product_team,
    read_product,
    get_party_key,
    read_spine_mhs_questionnaire,
    validate_spine_mhs_questionnaire_response,
    create_mhs_device,
    create_party_key_tag,
    add_spine_mhs_questionnaire_response,
    write_device,
    set_http_status,
]
