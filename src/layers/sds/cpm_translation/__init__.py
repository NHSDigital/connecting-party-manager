from itertools import chain
from typing import Generator
from uuid import UUID

from domain.core.aggregate_root import ExportedEventsTypeDef
from domain.core.device import Device, DeviceType
from domain.core.device_key import DeviceKeyType
from domain.core.questionnaire import Questionnaire
from domain.core.root import Root
from domain.core.validation import DEVICE_KEY_SEPARATOR
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs

DEFAULT_PRODUCT_TEAM = {
    "id": UUID(int=0x12345678123456781234567812345678),
    "name": "ROOT",
}
DEFAULT_ORGANISATION = "CDEF"


def update_in_list_of_dict(obj: list[dict[str, str]], key, value):
    for item in obj:
        if key in item:
            item[key] = value
            return
    obj.append({key: value})


def nhs_accredited_system_to_cpm_devices(
    nhs_accredited_system: NhsAccreditedSystem,
    questionnaire: Questionnaire,
    _questionnaire: dict,
    _trust: bool = False,
) -> Generator[Device, None, None]:
    ods_codes = nhs_accredited_system.nhs_as_client or [DEFAULT_ORGANISATION]
    unique_identifier = nhs_accredited_system.unique_identifier
    product_name = nhs_accredited_system.nhs_product_name or unique_identifier
    questionnaire_response_responses = (
        nhs_accredited_system.as_questionnaire_response_responses()
    )

    for ods_code in ods_codes:
        update_in_list_of_dict(
            obj=questionnaire_response_responses, key="nhs_as_client", value=[ods_code]
        )
        _questionnaire_response = questionnaire.respond(
            responses=questionnaire_response_responses
        )
        _organisation = Root.create_ods_organisation(ods_code=ods_code)
        _product_team = _organisation.create_product_team(**DEFAULT_PRODUCT_TEAM)
        _device = _product_team.create_device(
            name=product_name, type=DeviceType.PRODUCT, _trust=_trust
        )
        _device.add_key(
            type=DeviceKeyType.ACCREDITED_SYSTEM_ID,
            key=DEVICE_KEY_SEPARATOR.join((ods_code, unique_identifier)),
            _trust=_trust,
        )
        _device.add_questionnaire_response(
            questionnaire_response=_questionnaire_response,
            _questionnaire=_questionnaire,
            _trust=True,
        )
        yield _device


def nhs_mhs_to_cpm_device(
    nhs_mhs: NhsMhs,
    questionnaire: Questionnaire,
    _questionnaire: dict,
    _trust: bool = False,
) -> Device:
    party_key = nhs_mhs.nhs_mhs_party_key.strip()
    interaction_id = nhs_mhs.nhs_mhs_svc_ia.strip()
    ods_code = nhs_mhs.nhs_id_code
    scoped_party_key = DEVICE_KEY_SEPARATOR.join((ods_code, party_key, interaction_id))
    product_name = nhs_mhs.nhs_product_name or scoped_party_key
    questionnaire_response_responses = nhs_mhs.as_questionnaire_response_responses()
    questionnaire_response = questionnaire.respond(
        responses=questionnaire_response_responses
    )

    organisation = Root.create_ods_organisation(ods_code=ods_code)
    product_team = organisation.create_product_team(**DEFAULT_PRODUCT_TEAM)
    device = product_team.create_device(
        name=product_name, type=DeviceType.ENDPOINT, _trust=_trust
    )
    device.add_key(
        type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID,
        key=scoped_party_key,
        _trust=_trust,
    )
    device.add_questionnaire_response(
        questionnaire_response=questionnaire_response,
        _questionnaire=_questionnaire,
        _trust=True,
    )
    return device


def translate(
    obj: dict[str, str],
    spine_device_questionnaire: Questionnaire,
    _spine_device_questionnaire: dict,
    spine_endpoint_questionnaire: Questionnaire,
    _spine_endpoint_questionnaire: dict,
    _trust=False,
) -> ExportedEventsTypeDef:
    match obj["object_class"].lower():
        case NhsAccreditedSystem.OBJECT_CLASS:
            nhs_accredited_system = NhsAccreditedSystem.construct(**obj)
            devices = nhs_accredited_system_to_cpm_devices(
                nhs_accredited_system=nhs_accredited_system,
                questionnaire=spine_device_questionnaire,
                _questionnaire=_spine_device_questionnaire,
                _trust=_trust,
            )
        case NhsMhs.OBJECT_CLASS:
            nhs_mhs = NhsMhs.construct(**obj)
            devices = [
                nhs_mhs_to_cpm_device(
                    nhs_mhs=nhs_mhs,
                    questionnaire=spine_endpoint_questionnaire,
                    _questionnaire=_spine_endpoint_questionnaire,
                    _trust=_trust,
                )
            ]
        case _ as obj_type:
            raise NotImplementedError(
                f"No method implemented that translates object of type '{obj_type}'"
            )
    return list(chain.from_iterable(map(Device.export_events, devices)))
