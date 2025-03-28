from http import HTTPStatus

from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.sub_product import (
    parse_path_params,
    read_environment,
    read_product,
    read_product_team,
)
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.enum import Environment
from domain.core.epr_product import EprProduct
from domain.core.error import ConfigurationError
from domain.core.product_key import ProductKeyType
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.errors import AlreadyExistsError
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from domain.request_models import CreateDeviceReferenceAdditionalInteractionsDataParams
from domain.response.validation_errors import mark_validation_errors_as_inbound
from sds.epr.constants import ADDITIONAL_INTERACTIONS_SUFFIX, EprNameTemplate
from sds.epr.interactions import check_no_duplicate_interactions


@mark_validation_errors_as_inbound
def parse_device_reference_data_for_epr_payload(
    data, cache
) -> CreateDeviceReferenceAdditionalInteractionsDataParams:
    payload: dict = data[parse_event_body]
    return CreateDeviceReferenceAdditionalInteractionsDataParams(**payload)


def get_party_key(data, cache) -> str:
    product: EprProduct = data[read_product]
    party_keys = [
        key.key_value
        for key in product.keys
        if key.key_type is ProductKeyType.PARTY_KEY
    ]
    try:
        (party_key,) = party_keys
    except ValueError:
        raise ConfigurationError(
            "Not an EPR Product: Cannot create Additional Interactions in Product without exactly one Party Key"
        )
    return party_key


def require_no_existing_additional_interactions_device_reference_data(
    data, cache
) -> list[QuestionnaireResponse]:
    product: EprProduct = data[read_product]
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
        device_reference_data.name.endswith(ADDITIONAL_INTERACTIONS_SUFFIX)
        for device_reference_data in results
    ):
        raise AlreadyExistsError(
            "Additional Interactions Device Reference Data already exists for this Product"
        )


def read_questionnaire(data, cache) -> Questionnaire:
    return QuestionnaireRepository().read(
        QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    )


def validate_questionnaire_responses(data, cache) -> list[QuestionnaireResponse]:
    questionnaire: Questionnaire = data[read_questionnaire]
    payload: CreateDeviceReferenceAdditionalInteractionsDataParams = data[
        parse_device_reference_data_for_epr_payload
    ]
    raw_questionnaire_responses = payload.questionnaire_responses[
        QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
    ]
    return [questionnaire.validate(data=qr) for qr in raw_questionnaire_responses]


def require_unique_interactions(data, cache):
    check_no_duplicate_interactions(data[validate_questionnaire_responses])


def create_additional_interactions_device_reference_data(
    data, cache
) -> DeviceReferenceData:
    product: EprProduct = data[read_product]
    party_key: str = data[get_party_key]
    environment: Environment = data[read_environment]
    return product.create_device_reference_data(
        name=EprNameTemplate.ADDITIONAL_INTERACTIONS.format(party_key=party_key),
        environment=environment,
    )


def add_questionnaire_response(data, cache) -> list[QuestionnaireResponse]:
    questionnaire_responses: list[QuestionnaireResponse] = data[
        validate_questionnaire_responses
    ]
    device_reference_data: DeviceReferenceData = data[
        create_additional_interactions_device_reference_data
    ]
    for qr in questionnaire_responses:
        device_reference_data.add_questionnaire_response(qr)


def write_device_reference_data(data: dict[str, EprProduct], cache) -> EprProduct:
    device_reference_data: DeviceReferenceData = data[
        create_additional_interactions_device_reference_data
    ]
    repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return repo.write(device_reference_data)


def set_http_status(data, cache) -> tuple[HTTPStatus, str]:
    device_reference_data: DeviceReferenceData = data[
        create_additional_interactions_device_reference_data
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
    require_no_existing_additional_interactions_device_reference_data,
    read_questionnaire,
    validate_questionnaire_responses,
    require_unique_interactions,
    create_additional_interactions_device_reference_data,
    add_questionnaire_response,
    write_device_reference_data,
    set_http_status,
]
