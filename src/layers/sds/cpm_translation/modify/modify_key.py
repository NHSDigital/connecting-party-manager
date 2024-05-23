from dataclasses import astuple
from typing import Callable, Generator

import sds.domain
from domain.core.device import Device
from domain.core.device_key import DeviceKeyType
from domain.core.product_team import ProductTeam
from domain.core.validation import DEVICE_KEY_SEPARATOR
from sds.cpm_translation.utils import get_in_list_of_dict
from sds.domain.constants import ModificationType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import MessageHandlingSystemKey, NhsMhs

from ..constants import DEFAULT_PRODUCT_TEAM, UNIQUE_IDENTIFIER
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
            return new_accredited_system
        case (sds.domain.NhsAccreditedSystem, ModificationType.REPLACE):
            return replace_accredited_systems
        case (sds.domain.NhsMhs, ModificationType.REPLACE):
            return replace_msg_handling_system
        case _:
            raise InvalidModificationRequest(
                f"Forbidden to {modification_type} {model.__name__}.{field_name}",
            )


def new_accredited_system(
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

    _device = devices[0]
    (
        (questionnaire_id, (questionnaire_response,)),
    ) = _device.questionnaire_responses.items()
    new_questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=questionnaire_response,
        field_to_update=field_name,
        value=ods_code,
    )
    (unique_identifier,) = get_in_list_of_dict(
        obj=questionnaire_response.responses, key=UNIQUE_IDENTIFIER
    )
    new_accredited_system_id = DEVICE_KEY_SEPARATOR.join((ods_code, unique_identifier))

    product_team = ProductTeam(
        id=_device.product_team_id,
        ods_code=ods_code,
        name=DEFAULT_PRODUCT_TEAM["name"],
    )
    new_device = product_team.create_device(name=_device.name, type=_device.type)
    new_device.add_questionnaire_response(
        questionnaire_response=new_questionnaire_response
    )
    new_device.add_key(
        type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key=new_accredited_system_id
    )
    new_device.add_index(
        questionnaire_id=questionnaire_id, question_name=UNIQUE_IDENTIFIER
    )
    # "yield" to match the pattern of the functions returned by 'get_modify_key_function'
    # which may in general yield multiple deleted / added Devices
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

    (
        (questionnaire_id, (_questionnaire_response,)),
    ) = device.questionnaire_responses.items()
    new_value = NhsMhs.parse_and_validate_field(field=field_name, value=value)
    questionnaire_response = new_questionnaire_response_from_template(
        questionnaire_response=_questionnaire_response,
        field_to_update=field_name,
        value=new_value,
    )
    msg_handling_system_key = _get_msg_handling_system_key(
        responses=_questionnaire_response.responses
    )
    new_scoped_party_key = DEVICE_KEY_SEPARATOR.join(astuple(msg_handling_system_key))
    product_team = ProductTeam(
        id=device.product_team_id,
        ods_code=msg_handling_system_key.nhs_id_code,
        name=DEFAULT_PRODUCT_TEAM["name"],
    )
    new_device = product_team.create_device(name=device.name, type=device.type)
    new_device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    new_device.add_key(
        type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID, key=new_scoped_party_key
    )
    new_device.add_index(
        questionnaire_id=questionnaire_id, question_name=UNIQUE_IDENTIFIER
    )
    yield new_device
