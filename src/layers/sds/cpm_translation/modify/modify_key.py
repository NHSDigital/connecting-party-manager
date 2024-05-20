from typing import Callable, Generator

from domain.core.device import Device
from domain.core.device_key import DeviceKeyType
from domain.core.product_team import ProductTeam
from domain.core.validation import DEVICE_KEY_SEPARATOR
from sds.cpm_translation.utils import get_in_list_of_dict
from sds.domain.constants import ModificationType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs

from ..constants import DEFAULT_PRODUCT_TEAM
from .utils import InvalidModificationRequest, new_questionnaire_response_from_template


class NotAnSdsKey(Exception):
    pass


class AccreditedSystemAlreadyExists(Exception):
    def __init__(self, ods_code):
        super().__init__(f"Accredited System with ODS code '{ods_code}' already exists")


MHS_KEY_FIELDS = ["nhs_id_code", "nhs_mhs_party_key", "nhs_mhs_svc_ia"]


def get_modify_key_function(
    model: type[NhsMhs] | type[NhsAccreditedSystem],
    modification_type: ModificationType,
    field_name: str,
) -> Callable[[list[Device], str, any], Generator[Device, None, None]]:
    match (model, modification_type, field_name):
        case (
            NhsAccreditedSystem,
            ModificationType.ADD,
            "nhs_as_client",
        ):
            return new_accredited_system
        case (
            NhsAccreditedSystem,
            ModificationType.REPLACE,
            "nhs_as_client",
        ):
            return replace_accredited_systems
        case (
            NhsAccreditedSystem,
            ModificationType.DELETE,
            "nhs_as_client",
        ):
            raise InvalidModificationRequest(field_name)
        case (
            NhsMhs,
            ModificationType.ADD,
            "nhs_mhs_party_key" | "nhs_mhs_svc_ia" | "nhs_id_code",
        ):
            raise InvalidModificationRequest(field_name)
        case (
            NhsMhs,
            ModificationType.REPLACE,
            "nhs_mhs_party_key" | "nhs_mhs_svc_ia" | "nhs_id_code",
        ):
            return replace_msg_handling_system
        case (
            NhsMhs,
            ModificationType.DELETE,
            "nhs_mhs_party_key" | "nhs_mhs_svc_ia" | "nhs_id_code",
        ):
            raise InvalidModificationRequest(field_name)
        case _:
            raise NotAnSdsKey


def new_accredited_system(
    devices: list[Device], field_name: str, value: str
) -> Generator[Device, None, None]:
    (ods_code,) = NhsAccreditedSystem.parse_and_validate_field(
        field=field_name, value=value
    )

    current_ods_codes = {device.ods_code for device in devices}
    if ods_code in current_ods_codes:
        raise AccreditedSystemAlreadyExists(ods_code)

    device = devices[0]
    (
        (questionnaire_id, (questionnaire_response,)),
    ) = device.questionnaire_responses.items()
    new_questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=questionnaire_response,
        field_to_update=field_name,
        new_values=[ods_code],
    )
    unique_identifier = device.indexes[(questionnaire_id, "unique_identifier")]
    new_accredited_system_id = DEVICE_KEY_SEPARATOR.join((ods_code, unique_identifier))

    product_team = ProductTeam(
        id=device.product_team_id, ods_code=ods_code, name=DEFAULT_PRODUCT_TEAM["name"]
    )
    new_device = product_team.create_device(name=device.name, type=device.type)
    new_device.add_questionnaire_response(
        questionnaire_response=new_questionnaire_response
    )
    new_device.add_key(
        type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key=new_accredited_system_id
    )
    new_device.add_index(
        questionnaire_id=questionnaire_id, question_name="unique_identifier"
    )
    yield new_device


def replace_accredited_systems(
    devices: list[Device], field_name: str, value: str
) -> Generator[Device, None, None]:
    current_ods_codes = {device.ods_code for device in devices}
    final_ods_codes = NhsAccreditedSystem.parse_and_validate_field(
        field=field_name, value=value
    )
    removed_ods_codes = current_ods_codes - final_ods_codes
    for device in devices:
        if device.ods_code in removed_ods_codes:
            device.delete()
        yield device

    for new_ods_code in final_ods_codes - current_ods_codes:
        yield from new_accredited_system(
            devices=devices, field_name=field_name, value=[new_ods_code]
        )


def _get_msg_handling_system_scoped_key_parts(
    responses: list[dict],
) -> Generator[str, None, None]:
    for key_field in MHS_KEY_FIELDS:
        (_value,) = get_in_list_of_dict(obj=responses, key=key_field)
        yield _value.strip()


def replace_msg_handling_system(
    devices: list[Device], field_name: str, value: str
) -> Generator[Device, None, None]:
    (device,) = devices
    device.delete()
    yield device

    (
        (questionnaire_id, (_questionnaire_response,)),
    ) = device.questionnaire_responses.items()
    new_value = NhsMhs.parse_and_validate_field(field=field_name, value=value)
    new_questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=_questionnaire_response,
        field_to_update=field_name,
        new_values=[new_value],
    )
    key_parts = _get_msg_handling_system_scoped_key_parts(
        responses=_questionnaire_response.responses
    )
    new_scoped_party_key = DEVICE_KEY_SEPARATOR.join(key_parts)
    (ods_code,) = get_in_list_of_dict(
        obj=_questionnaire_response.responses, key="nhs_id_code"
    )

    product_team = ProductTeam(
        id=device.product_team_id, ods_code=ods_code, name=DEFAULT_PRODUCT_TEAM["name"]
    )
    new_device = product_team.create_device(name=device.name, type=device.type)
    new_device.add_questionnaire_response(
        questionnaire_response=new_questionnaire_response
    )
    new_device.add_key(
        type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID, key=new_scoped_party_key
    )
    new_device.add_index(
        questionnaire_id=questionnaire_id, question_name="unique_identifier"
    )
    yield new_device
