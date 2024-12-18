from http import HTTPStatus

from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.questionnaire_response_validation import (
    process_and_validate_questionnaire_response,
)
from domain.api.common_steps.read_product import (
    get_party_key,
    parse_path_params,
    read_product,
    read_product_team,
)
from domain.core.cpm_product import CpmProduct
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.errors import AlreadyExistsError
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from domain.request_models import CreateDeviceReferenceMessageSetsDataParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from sds.epr.constants import MESSAGE_SETS_SUFFIX, EprNameTemplate


@mark_validation_errors_as_inbound
def parse_device_reference_data_for_epr_payload(
    data, cache
) -> CreateDeviceReferenceMessageSetsDataParams:
    payload: dict = data[parse_event_body]
    return CreateDeviceReferenceMessageSetsDataParams(**payload)


def require_no_existing_message_sets_device_reference_data(
    data, cache
) -> list[QuestionnaireResponse]:
    product: CpmProduct = data[read_product]
    repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = repo.search(
        product_team_id=product.product_team_id, product_id=product.id
    )
    if any(
        device_reference_data.name.endswith(MESSAGE_SETS_SUFFIX)
        for device_reference_data in results
    ):
        raise AlreadyExistsError(
            "This product already has a 'Message Sets' DeviceReferenceData. "
            "Please update, or delete and recreate if you wish to make changes."
        )


def read_spine_mhs_message_sets_questionnaire(data, cache) -> Questionnaire:
    return QuestionnaireRepository().read(QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS)


def validate_questionnaire_responses(data, cache) -> list[QuestionnaireResponse]:
    questionnaire: Questionnaire = data[read_spine_mhs_message_sets_questionnaire]
    payload: CreateDeviceReferenceMessageSetsDataParams = data[
        parse_device_reference_data_for_epr_payload
    ]
    raw_questionnaire_responses = payload.questionnaire_responses[
        QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
    ]
    party_key = data[get_party_key]

    validated_responses = [
        process_and_validate_questionnaire_response(
            questionnaire,
            qr,
            party_key,
            instance=QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS,
        )
        for qr in raw_questionnaire_responses
    ]

    return validated_responses


def create_message_set_device_reference_data(data, cache) -> DeviceReferenceData:
    product: CpmProduct = data[read_product]
    party_key: str = data[get_party_key]
    return product.create_device_reference_data(
        name=EprNameTemplate.MESSAGE_SETS.format(party_key=party_key)
    )


def add_questionnaire_response(data, cache) -> list[QuestionnaireResponse]:
    questionnaire_responses: list[QuestionnaireResponse] = data[
        validate_questionnaire_responses
    ]
    device_reference_data: DeviceReferenceData = data[
        create_message_set_device_reference_data
    ]
    for qr in questionnaire_responses:
        device_reference_data.add_questionnaire_response(qr)


def write_device_reference_data(data: dict[str, CpmProduct], cache) -> CpmProduct:
    device_reference_data: DeviceReferenceData = data[
        create_message_set_device_reference_data
    ]
    repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return repo.write(device_reference_data)


def set_http_status(data, cache) -> tuple[HTTPStatus, str]:
    device_reference_data: DeviceReferenceData = data[
        create_message_set_device_reference_data
    ]
    return HTTPStatus.CREATED, device_reference_data.state()


steps = [
    parse_event_body,
    parse_path_params,
    parse_device_reference_data_for_epr_payload,
    read_product_team,
    read_product,
    get_party_key,
    require_no_existing_message_sets_device_reference_data,
    read_spine_mhs_message_sets_questionnaire,
    validate_questionnaire_responses,
    create_message_set_device_reference_data,
    add_questionnaire_response,
    write_device_reference_data,
    set_http_status,
]
