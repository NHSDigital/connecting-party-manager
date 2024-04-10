from typing import Generator
from uuid import UUID

from domain.core.device import Device, DeviceType
from domain.core.device_key import DeviceKeyType
from domain.core.product_team import ProductTeam
from domain.core.questionnaire import Questionnaire
from domain.core.root import Root
from domain.core.validation import DEVICE_KEY_SEPARATOR
from domain.repository.device_repository import DeviceRepository
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs

DEFAULT_PRODUCT_TEAM = {
    "id": UUID(int=0x12345678123456781234567812345678),
    "name": "ROOT",
}
EXCEPTIONAL_ODS_CODES = {
    "696B001",
    "TESTEBS1",
    "TESTLSP0",
    "TESTLSP1",
    "TESTLSP3",
    "TMSAsync1",
    "TMSAsync2",
    "TMSAsync3",
    "TMSAsync4",
    "TMSAsync5",
    "TMSAsync6",
    "TMSEbs2",
}

DEFAULT_ORGANISATION = "CDEF"


def accredited_system_ids(
    nhs_accredited_system: NhsAccreditedSystem,
) -> Generator[tuple[str, str], None, None]:
    for ods_code in nhs_accredited_system.nhs_as_client or [DEFAULT_ORGANISATION]:
        yield ods_code, DEVICE_KEY_SEPARATOR.join(
            (ods_code, nhs_accredited_system.unique_identifier)
        )


def scoped_party_key(nhs_mhs: NhsMhs) -> str:
    party_key = nhs_mhs.nhs_mhs_party_key.strip()
    interaction_id = nhs_mhs.nhs_mhs_svc_ia.strip()
    ods_code = nhs_mhs.nhs_id_code
    return DEVICE_KEY_SEPARATOR.join((ods_code, party_key, interaction_id))


def update_in_list_of_dict(obj: list[dict[str, str]], key, value):
    for item in obj:
        if key in item:
            item[key] = value
            return
    obj.append({key: value})


def create_product_team(ods_code: str) -> ProductTeam:
    if ods_code in EXCEPTIONAL_ODS_CODES:
        product_team = ProductTeam(**DEFAULT_PRODUCT_TEAM, ods_code=ods_code)
    else:
        organisation = Root.create_ods_organisation(ods_code=ods_code)
        product_team = organisation.create_product_team(**DEFAULT_PRODUCT_TEAM)
    return product_team


def nhs_accredited_system_to_cpm_devices(
    nhs_accredited_system: NhsAccreditedSystem,
    questionnaire: Questionnaire,
    _questionnaire: dict,
    _trust: bool = False,
    **extra
) -> Generator[Device, None, None]:
    unique_identifier = nhs_accredited_system.unique_identifier
    product_name = nhs_accredited_system.nhs_product_name or unique_identifier
    questionnaire_response_responses = (
        nhs_accredited_system.as_questionnaire_response_responses()
    )

    for (
        ods_code,
        accredited_system_id,
    ) in accredited_system_ids(nhs_accredited_system):
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
            key=accredited_system_id,
            _trust=_trust,
        )
        _device.add_questionnaire_response(
            questionnaire_response=_questionnaire_response,
            _questionnaire=_questionnaire,
            _trust=True,
        )
        yield _device


def modify_accredited_system_devices(
    nhs_accredited_system: NhsAccreditedSystem, repository: DeviceRepository, **extra
) -> Generator[Device, None, None]:
    for (
        _,
        accredited_system_id,
    ) in accredited_system_ids(nhs_accredited_system):
        device = repository.read_by_key(key=accredited_system_id)
        device.update(something="foo")
        yield device


def delete_accredited_system_devices(
    nhs_accredited_system: NhsAccreditedSystem, repository: DeviceRepository, **extra
):
    for (
        _,
        accredited_system_id,
    ) in accredited_system_ids(nhs_accredited_system):
        device = repository.read_by_key(key=accredited_system_id)
        device.delete()
        yield device


def nhs_mhs_to_cpm_device(
    nhs_mhs: NhsMhs,
    questionnaire: Questionnaire,
    _questionnaire: dict,
    _trust: bool = False,
    **extra
) -> Device:
    ods_code = nhs_mhs.nhs_id_code
    _scoped_party_key = scoped_party_key(nhs_mhs)
    product_name = nhs_mhs.nhs_product_name or _scoped_party_key
    questionnaire_response_responses = nhs_mhs.as_questionnaire_response_responses()
    questionnaire_response = questionnaire.respond(
        responses=questionnaire_response_responses
    )

    product_team = create_product_team(ods_code=ods_code)
    device = product_team.create_device(
        name=product_name, type=DeviceType.ENDPOINT, _trust=_trust
    )
    device.add_key(
        type=DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID,
        key=_scoped_party_key,
        _trust=_trust,
    )
    device.add_questionnaire_response(
        questionnaire_response=questionnaire_response,
        _questionnaire=_questionnaire,
        _trust=True,
    )
    return device


def modify_mhs_device(nhs_mhs: NhsMhs, repository: DeviceRepository, **extra):
    device = repository.read_by_key(key=scoped_party_key(nhs_mhs))
    device.update(something="foo")
    return device


def delete_mhs_device(nhs_mhs: NhsMhs, repository: DeviceRepository, **extra):
    device = repository.read_by_key(key=scoped_party_key(nhs_mhs))
    device.delete()
    return device
