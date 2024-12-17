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
from domain.core.device import (
    Device,
    DeviceKeyAddedEvent,
    DeviceReferenceDataIdAddedEvent,
    DeviceTagAddedEvent,
    QuestionnaireResponseUpdatedEvent,
)
from domain.core.device_key import DeviceKeyType
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.enum import Environment
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
from sds.epr.constants import EprNameTemplate, SdsDeviceReferenceDataPath, SdsFieldName


@mark_validation_errors_as_inbound
def parse_mhs_device_payload(data, cache) -> CreateMhsDeviceIncomingParams:
    payload: dict = data[parse_event_body]
    return CreateMhsDeviceIncomingParams(**payload)


def check_for_existing_mhs(data, cache):
    product_team: ProductTeam = data[read_product_team]
    product: CpmProduct = data[read_product]
    environment: Environment = data[read_environment]
    party_key: str = data[get_party_key]

    device_repo = DeviceRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )

    devices = device_repo.search(
        product_team_id=product_team.id, product_id=product.id, environment=environment
    )
    if any(
        device.name == EprNameTemplate.MHS_DEVICE.format(party_key=party_key)
        for device in devices
    ):
        raise ConfigurationError(
            "There is already an existing MHS Device for this Product"
        )


def read_device_reference_data(data, cache) -> DeviceReferenceData:
    path_params: CpmProductPathParams = data[parse_path_params]
    environment: Environment = data[read_environment]
    drd_repo = DeviceReferenceDataRepository(
        table_name=cache["DYNAMODB_TABLE"], dynamodb_client=cache["DYNAMODB_CLIENT"]
    )
    device_reference_datas = drd_repo.search(
        product_id=path_params.product_id,
        product_team_id=path_params.product_team_id,
        environment=environment,
    )

    party_key: str = data[get_party_key]
    try:
        (device_reference_data,) = filter(
            lambda drd: drd.name
            == EprNameTemplate.MESSAGE_SETS.format(party_key=party_key),
            device_reference_datas,
        )
    except ValueError:
        raise ConfigurationError(
            "You must configure exactly one MessageSet Device Reference Data before creating an MHS Device."
        )
    return device_reference_data


def read_spine_mhs_questionnaire(data, cache) -> Questionnaire:
    return QuestionnaireRepository().read(QuestionnaireInstance.SPINE_MHS)


def validate_spine_mhs_questionnaire_response(data, cache) -> QuestionnaireResponse:
    questionnaire: Questionnaire = data[read_spine_mhs_questionnaire]
    payload: CreateMhsDeviceIncomingParams = data[parse_mhs_device_payload]
    raw_questionnaire_responses = payload.questionnaire_responses[
        QuestionnaireInstance.SPINE_MHS
    ]

    if len(raw_questionnaire_responses) != 1:
        raise ConfigurationError(
            "You must provide exactly one spine_mhs questionnaire response to create an MHS Device."
        )
    party_key = data[get_party_key]

    validated_responses = [
        process_and_validate_questionnaire_response(
            questionnaire, qr, party_key, instance=QuestionnaireInstance.SPINE_MHS
        )
        for qr in raw_questionnaire_responses
    ]

    return validated_responses


def create_mhs_device(data, cache) -> Device:
    product: CpmProduct = data[read_product]
    party_key: str = data[get_party_key]
    payload: CreateMhsDeviceIncomingParams = data[parse_mhs_device_payload]
    environment: Environment = data[read_environment]
    # payload.__dict__["env"] = data[read_environment]

    # Create a new Device dictionary excluding 'questionnaire_responses'
    device_payload = payload.dict(exclude={"questionnaire_responses"})
    return product.create_device(
        name=EprNameTemplate.MHS_DEVICE.format(party_key=party_key),
        env=environment,
        **device_payload,
    )


def create_party_key_tag(data, cache) -> DeviceTagAddedEvent:
    mhs_device: Device = data[create_mhs_device]
    return mhs_device.add_tag(party_key=data[get_party_key])


def create_cpa_id_keys(data, cache) -> DeviceKeyAddedEvent:
    mhs_device: Device = data[create_mhs_device]
    drd: DeviceReferenceData = data[read_device_reference_data]

    questionnaire_responses = drd.questionnaire_responses.get(
        f"{QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS}/1", []
    )

    cpa_ids = [
        response.data.get(SdsFieldName.CPA_ID) for response in questionnaire_responses
    ]

    for id in cpa_ids:
        mhs_device.add_key(key_type=DeviceKeyType.CPA_ID, key_value=id)

    return mhs_device


def add_device_reference_data_id(data, cache) -> DeviceReferenceDataIdAddedEvent:
    mhs_device: Device = data[create_mhs_device]
    drd: DeviceReferenceData = data[read_device_reference_data]
    return mhs_device.add_device_reference_data_id(
        device_reference_data_id=str(drd.id),
        path_to_data=[SdsDeviceReferenceDataPath.ALL],
    )


def add_spine_mhs_questionnaire_response(
    data, cache
) -> QuestionnaireResponseUpdatedEvent:
    spine_mhs_questionnaire_response: list[QuestionnaireResponse] = data[
        validate_spine_mhs_questionnaire_response
    ]
    mhs_device: Device = data[create_mhs_device]

    for qr in spine_mhs_questionnaire_response:
        mhs_device.add_questionnaire_response(qr)


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
    read_environment,
    parse_mhs_device_payload,
    read_product_team,
    read_product,
    get_party_key,
    check_for_existing_mhs,
    read_spine_mhs_questionnaire,
    read_device_reference_data,
    validate_spine_mhs_questionnaire_response,
    create_mhs_device,
    create_party_key_tag,
    create_cpa_id_keys,
    add_device_reference_data_id,
    add_spine_mhs_questionnaire_response,
    write_device,
    set_http_status,
]
