from http import HTTPStatus

from domain.api.common_steps.general import parse_event_body
from domain.api.common_steps.read_product import (
    get_party_key,
    parse_path_params,
    read_product,
    read_product_team,
)
from domain.core.cpm_product import CpmProduct
from domain.core.device import (
    MHS_DEVICE_NAME,
    Device,
    DeviceKeyAddedEvent,
    DeviceReferenceDataIdAddedEvent,
    DeviceTagAddedEvent,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.device_key import DeviceKeyType
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.error import ConfigurationError
from domain.core.product_team import ProductTeam
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository import DeviceRepository
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from domain.request_models import CpmProductPathParams, CreateMhsDeviceIncomingParams
from domain.response.validation_errors import mark_validation_errors_as_inbound


@mark_validation_errors_as_inbound
def parse_mhs_device_payload(data, cache) -> CreateMhsDeviceIncomingParams:
    payload: dict = data[parse_event_body]
    return CreateMhsDeviceIncomingParams(**payload)


def check_for_existing_mhs(data, cache):
    product_team: ProductTeam = data[read_product_team]
    product: CpmProduct = data[read_product]

    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )

    devices = device_repo.search(product_team_id=product_team.id, product_id=product.id)
    if any(device.name == MHS_DEVICE_NAME for device in devices):
        raise ConfigurationError(
            "There is already an existing MHS Device for this Product"
        )


def read_device_reference_data(data, cache) -> DeviceReferenceData:
    path_params: CpmProductPathParams = data[parse_path_params]
    drd_repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    device_reference_datas = drd_repo.search(
        product_id=path_params.product_id,
        product_team_id=path_params.product_team_id,
    )

    party_key: str = data[get_party_key]
    # use {QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS}
    mhs_message_set_drd_name = f"{party_key} - MHS Message Set"

    try:
        (device_reference_data,) = filter(
            lambda drd: drd.name == mhs_message_set_drd_name, device_reference_datas
        )
    except ValueError:
        raise ConfigurationError(
            "You must configure exactly one MessageSet Device Reference Data before creating an MHS Device"
        )
    return device_reference_data


def read_spine_mhs_questionnaire(data, cache) -> Questionnaire:
    return QuestionnaireRepository().read(QuestionnaireInstance.SPINE_MHS)


def validate_spine_mhs_questionnaire_response(data, cache) -> QuestionnaireResponse:
    spine_mhs_questionnaire: Questionnaire = data[read_spine_mhs_questionnaire]
    payload: CreateMhsDeviceIncomingParams = data[parse_mhs_device_payload]

    spine_mhs_questionnaire_response = payload.questionnaire_responses[
        QuestionnaireInstance.SPINE_MHS
    ]

    return spine_mhs_questionnaire.validate(
        data=spine_mhs_questionnaire_response.__root__[0]
    )


def create_mhs_device(data, cache) -> Device:
    product: CpmProduct = data[read_product]
    payload: CreateMhsDeviceIncomingParams = data[parse_mhs_device_payload]

    # Create a new Device dictionary excluding 'questionnaire_responses'
    device_payload = payload.dict(exclude={"questionnaire_responses"})
    return product.create_device(**device_payload)


def create_party_key_tag(data, cache) -> DeviceTagAddedEvent:
    mhs_device: Device = data[create_mhs_device]
    return mhs_device.add_tag(party_key=data[get_party_key])


def create_cpa_id_keys(data, cache) -> DeviceKeyAddedEvent:
    mhs_device: Device = data[create_mhs_device]
    party_key = data[get_party_key]
    drd: DeviceReferenceData = data[read_device_reference_data]
    interaction_ids = []

    # Extract Interaction IDs from questionnaire responses
    questionnaire_responses = drd.questionnaire_responses.get(
        f"{QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS}/1", []
    )
    for response in questionnaire_responses:
        interaction_ids.append(response.data.get("Interaction ID"))

    # Use cpa_id in furture
    for id in interaction_ids:
        mhs_device.add_key(
            key_type=DeviceKeyType.INTERACTION_ID, key_value=f"{party_key}:{id}"
        )

    return mhs_device


def add_device_reference_data_id(data, cache) -> DeviceReferenceDataIdAddedEvent:
    mhs_device: Device = data[create_mhs_device]
    drd: DeviceReferenceData = data[read_device_reference_data]
    return mhs_device.add_device_reference_data_id(
        device_reference_data_id=str(drd.id), path_to_data=["*"]
    )


def add_spine_mhs_questionnaire_response(
    data, cache
) -> QuestionnaireResponseUpdatedEvent:
    spine_mhs_questionnaire_response: QuestionnaireResponse = data[
        validate_spine_mhs_questionnaire_response
    ]
    mhs_device: Device = data[create_mhs_device]

    return mhs_device.add_questionnaire_response(spine_mhs_questionnaire_response)


def write_device(data: dict[str, Device], cache) -> Device:
    mhs_device: Device = data[create_mhs_device]
    repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    return repo.write(mhs_device)


def set_http_status(data, cache) -> tuple[HTTPStatus, dict]:
    mhs_device: Device = data[create_mhs_device]
    return HTTPStatus.CREATED, mhs_device.state_exclude_tags()


steps = [
    parse_event_body,
    parse_path_params,
    parse_mhs_device_payload,
    read_product_team,
    read_product,
    get_party_key,
    check_for_existing_mhs,
    read_device_reference_data,
    read_spine_mhs_questionnaire,
    validate_spine_mhs_questionnaire_response,
    create_mhs_device,
    create_party_key_tag,
    create_cpa_id_keys,
    add_device_reference_data_id,
    add_spine_mhs_questionnaire_response,
    write_device,
    set_http_status,
]
