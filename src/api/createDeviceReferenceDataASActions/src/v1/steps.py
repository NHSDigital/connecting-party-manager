from http import HTTPStatus

from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.read_product import (
    parse_path_params,
    read_product,
    read_product_team,
)
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.error import ConfigurationError
from domain.core.product_key.v1 import ProductKeyType
from domain.core.questionnaire.v3 import Questionnaire, QuestionnaireResponse
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.errors import AlreadyExistsError
from domain.repository.questionnaire_repository.v2 import QuestionnaireRepository
from domain.repository.questionnaire_repository.v2.questionnaires import (
    QuestionnaireInstance,
)
from domain.request_models.v1 import (
    CreateDeviceReferenceAdditionalInteractionsDataParams,
)
from domain.response.validation_errors import mark_validation_errors_as_inbound

DEVICE_NAME_MARKER = "AS Additional Interactions"


@mark_validation_errors_as_inbound
def parse_device_reference_data_for_epr_payload(
    data, cache
) -> CreateDeviceReferenceAdditionalInteractionsDataParams:
    payload: dict = data[parse_event_body]
    return CreateDeviceReferenceAdditionalInteractionsDataParams(**payload)


def get_party_key(data, cache) -> str:
    product: CpmProduct = data[read_product]
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
    product: CpmProduct = data[read_product]
    repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    results = repo.search(
        product_team_id=product.product_team_id, product_id=product.id
    )
    if any(
        device_reference_data.name.endswith(DEVICE_NAME_MARKER)
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


def create_additional_interactions_device_reference_data(
    data, cache
) -> DeviceReferenceData:
    product: CpmProduct = data[read_product]
    party_key: str = data[get_party_key]
    return product.create_device_reference_data(
        name=f"{party_key} - {DEVICE_NAME_MARKER}"
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


def write_device_reference_data(data: dict[str, CpmProduct], cache) -> CpmProduct:
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
    parse_device_reference_data_for_epr_payload,
    read_product_team,
    read_product,
    get_party_key,
    require_no_existing_additional_interactions_device_reference_data,
    read_questionnaire,
    validate_questionnaire_responses,
    create_additional_interactions_device_reference_data,
    add_questionnaire_response,
    write_device_reference_data,
    set_http_status,
]
