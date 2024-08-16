from dataclasses import astuple
from typing import Callable, Generator

import sds.domain
from domain.api.sds.query import (
    SearchSDSDeviceQueryParams,
    SearchSDSEndpointQueryParams,
)
from domain.core.device.v2 import Device
from domain.core.device_key.v2 import DeviceKeyType
from domain.core.product_team.v2 import ProductTeam
from domain.core.validation import DEVICE_KEY_SEPARATOR
from sds.cpm_translation.utils import get_in_list_of_dict, set_device_tags
from sds.domain.constants import ModificationType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import MessageHandlingSystemKey, NhsMhs

from .constants import DEFAULT_PRODUCT_TEAM, UNIQUE_IDENTIFIER
from .modify_device import new_questionnaire_response_from_template


class AccreditedSystemAlreadyExists(Exception):
    ...


class NotAnSdsKey(Exception):
    ...


class InvalidModificationRequest(Exception):
    ...


def get_modify_key_function(
    model: type[NhsMhs] | type[NhsAccreditedSystem],
    modification_type: ModificationType,
    field_name: str,
) -> Callable[[list[Device], str, any], Generator[Device, None, None]]:
    """Returns a function which yields deleted and created Devices"""
    if not model.is_key_field(field_name):
        raise NotAnSdsKey(field_name)

    match (model, modification_type):
        case (sds.domain.NhsAccreditedSystem, ModificationType.ADD):
            return copy_new_accredited_system_from_sibling_device
        case (sds.domain.NhsAccreditedSystem, ModificationType.REPLACE):
            return replace_accredited_systems
        case (sds.domain.NhsMhs, ModificationType.REPLACE):
            return replace_msg_handling_system
        case _:
            raise InvalidModificationRequest(
                f"Forbidden to {modification_type} {model.__name__}.{field_name}",
            )


def copy_new_accredited_system_from_sibling_device(
    devices: list[Device], field_name: str, value: str
) -> Generator[Device, None, None]:
    (ods_code,) = NhsAccreditedSystem.parse_and_validate_field(
        field=field_name, value=value
    )

    current_ods_codes = {device.ods_code for device in devices}
    if ods_code in current_ods_codes:
        raise AccreditedSystemAlreadyExists(
            f"Accredited System with ODS code '{ods_code}' already exists"
        )

    _device = devices[0]  # could copy any sibling, but pick the 0th one as convention

    (questionnaire_response_by_datetime,) = _device.questionnaire_responses.values()
    (questionnaire_response,) = questionnaire_response_by_datetime.values()
    questionnaire_response.questionnaire = NhsAccreditedSystem.questionnaire()

    new_questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=questionnaire_response,
        field_to_update=field_name,
        value=ods_code,
    )
    (unique_identifier,) = get_in_list_of_dict(
        obj=questionnaire_response.answers, key=UNIQUE_IDENTIFIER
    )
    new_accredited_system_id = DEVICE_KEY_SEPARATOR.join((ods_code, unique_identifier))

    product_team = ProductTeam(
        id=_device.product_team_id,
        ods_code=ods_code,
        name=DEFAULT_PRODUCT_TEAM["name"],
    )
    new_device = product_team.create_device(
        name=_device.name, device_type=_device.device_type
    )
    new_device.add_questionnaire_response(
        questionnaire_response=new_questionnaire_response
    )
    new_device.add_key(
        key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value=new_accredited_system_id
    )
    set_device_tags(
        device=new_device,
        data=new_questionnaire_response.flat_answers,
        model=SearchSDSDeviceQueryParams,
    )

    # "yield" to match the pattern of the functions returned by 'get_modify_key_function'
    # which may in general yield multiple deleted / added Devices
    for device in devices:
        yield device
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
        *_, new_device = copy_new_accredited_system_from_sibling_device(
            devices=devices, field_name=field_name, value=[new_ods_code]
        )
        yield new_device


def _get_msg_handling_system_key(responses: list[dict]) -> MessageHandlingSystemKey:
    """Construct the MHS scoped party key from questionnaire responses"""
    return MessageHandlingSystemKey(
        **{
            key: values
            for key in NhsMhs.key_fields()
            for values in get_in_list_of_dict(obj=responses, key=key)
        }
    )


def replace_msg_handling_system(
    devices: list[Device], field_name: str, value: str
) -> Generator[Device, None, None]:
    (device,) = devices
    device.delete()
    yield device

    (questionnaire_response_by_datetime,) = device.questionnaire_responses.values()
    (_questionnaire_response,) = questionnaire_response_by_datetime.values()
    _questionnaire_response.questionnaire = NhsMhs.questionnaire()

    new_value = NhsMhs.parse_and_validate_field(field=field_name, value=value)
    questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=_questionnaire_response,
        field_to_update=field_name,
        value=new_value,
    )
    msg_handling_system_key = _get_msg_handling_system_key(
        responses=_questionnaire_response.answers
    )
    new_scoped_party_key = DEVICE_KEY_SEPARATOR.join(astuple(msg_handling_system_key))
    product_team = ProductTeam(
        id=device.product_team_id,
        ods_code=msg_handling_system_key.nhs_id_code,
        name=DEFAULT_PRODUCT_TEAM["name"],
    )
    new_device = product_team.create_device(
        name=device.name, device_type=device.device_type
    )
    new_device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    new_device.add_key(
        key_type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID,
        key_value=new_scoped_party_key,
    )
    set_device_tags(
        device=new_device,
        data=questionnaire_response.flat_answers,
        model=SearchSDSEndpointQueryParams,
    )

    yield new_device
