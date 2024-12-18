from http import HTTPStatus

from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.questionnaire_response_validation import (
    process_and_validate_questionnaire_response,
)
from domain.api.common_steps.sub_product import (
    get_party_key,
    parse_path_params,
    read_environment,
    read_product,
    read_product_team,
)
from domain.core.cpm_product import CpmProduct
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.enum import Environment
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from domain.questionnaire_instances.strategies import (
    generate_spine_mhs_message_sets_fields,
)
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
from sds.epr.interactions import check_no_duplicate_interactions


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
    environment: Environment = data[read_environment]
    repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = repo.search(
        product_team_id=product.product_team_id,
        product_id=product.id,
        environment=environment,
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
            questionnaire=questionnaire,
            questionnaire_response=qr,
            generation_strategy=generate_spine_mhs_message_sets_fields,
            party_key=party_key,
        )
        for qr in raw_questionnaire_responses
    ]

    return validated_responses


def require_unique_interactions(data, cache):
    check_no_duplicate_interactions(data[validate_questionnaire_responses])


def create_message_set_device_reference_data(data, cache) -> DeviceReferenceData:
    product: CpmProduct = data[read_product]
    party_key: str = data[get_party_key]
    environment: Environment = data[read_environment]
    return product.create_device_reference_data(
        name=EprNameTemplate.MESSAGE_SETS.format(party_key=party_key),
        environment=environment,
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
    read_environment,
    parse_device_reference_data_for_epr_payload,
    read_product_team,
    read_product,
    get_party_key,
    require_no_existing_message_sets_device_reference_data,
    read_spine_mhs_message_sets_questionnaire,
    validate_questionnaire_responses,
    require_unique_interactions,
    create_message_set_device_reference_data,
    add_questionnaire_response,
    write_device_reference_data,
    set_http_status,
]
