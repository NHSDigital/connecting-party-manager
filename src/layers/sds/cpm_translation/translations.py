from functools import partial
from itertools import filterfalse
from typing import Generator

from domain.core.device import Device, DeviceType
from domain.core.device_key import DeviceKeyType
from domain.core.product_team import ProductTeam
from domain.core.questionnaire import Questionnaire
from domain.core.root import Root
from domain.core.validation import DEVICE_KEY_SEPARATOR
from domain.repository.device_repository import DeviceRepository
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import MHS_SCOPED_PARTY_KEY_FIELDS, NhsMhs
from sds.domain.sds_deletion_request import SdsDeletionRequest
from sds.domain.sds_modification_request import SdsModificationRequest

from .constants import (
    DEFAULT_ORGANISATION,
    DEFAULT_PRODUCT_TEAM,
    EXCEPTIONAL_ODS_CODES,
    UNIQUE_IDENTIFIER,
)
from .modify.modify_device import update_device_metadata
from .modify.modify_key import NotAnSdsKey, get_modify_key_function
from .utils import update_in_list_of_dict


def accredited_system_ids(
    nhs_accredited_system: NhsAccreditedSystem,
) -> Generator[tuple[str, str], None, None]:
    for ods_code in nhs_accredited_system.nhs_as_client or [DEFAULT_ORGANISATION]:
        yield ods_code, DEVICE_KEY_SEPARATOR.join(
            (ods_code, nhs_accredited_system.unique_identifier)
        )


def scoped_party_key(nhs_mhs: NhsMhs) -> str:
    return DEVICE_KEY_SEPARATOR.join(
        getattr(nhs_mhs, key) for key in MHS_SCOPED_PARTY_KEY_FIELDS
    )


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
        _device.add_index(
            questionnaire_id=questionnaire.id, question_name=UNIQUE_IDENTIFIER
        )
        yield _device


def nhs_mhs_to_cpm_device(
    nhs_mhs: NhsMhs,
    questionnaire: Questionnaire,
    _questionnaire: dict,
    _trust: bool = False,
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
    device.add_index(questionnaire_id=questionnaire.id, question_name=UNIQUE_IDENTIFIER)
    return device


class NoDeviceFound(Exception):
    pass


def read_devices_by_unique_identifier(
    questionnaire_ids: list[str], repository: DeviceRepository, value: str
) -> Generator[Device, None, None]:
    for questionnaire_id in questionnaire_ids:
        for device in repository.read_by_index(
            questionnaire_id=questionnaire_id,
            question_name=UNIQUE_IDENTIFIER,
            value=value,
        ):
            if device.is_active():
                yield device


def modify_devices(
    modification_request: SdsModificationRequest,
    questionnaire_ids: list[str],
    repository: DeviceRepository,
) -> Generator[Device, None, None]:
    devices = list(
        read_devices_by_unique_identifier(
            questionnaire_ids=questionnaire_ids,
            repository=repository,
            value=modification_request.unique_identifier,
        )
    )
    # Only apply modifications if there are devices to modify
    modifications = modification_request.modifications if devices else []

    _devices = devices
    for modification_type, field, new_values in modifications:
        device_type = _devices[0].type
        model = NhsAccreditedSystem if device_type is DeviceType.PRODUCT else NhsMhs
        field_name = model.get_field_name_for_alias(alias=field)

        try:
            modify_key = get_modify_key_function(
                model=model,
                field_name=field_name,
                modification_type=modification_type,
            )
            _devices += list(
                modify_key(devices=_devices, field_name=field_name, value=new_values)
            )
        except NotAnSdsKey:
            update_metadata = partial(
                update_device_metadata,
                model=model,
                modification_type=modification_type,
                field_alias=field,
                new_values=new_values,
            )
            _active_devices = list(filter(Device.is_active, _devices))
            _inactive_devices = list(filterfalse(Device.is_active, _devices))
            _devices = [*map(update_metadata, _active_devices), *_inactive_devices]
    yield from _devices


def delete_devices(
    deletion_request: SdsDeletionRequest,
    questionnaire_ids: list[str],
    repository: DeviceRepository,
) -> list[Device]:
    devices = []
    for _device in read_devices_by_unique_identifier(
        questionnaire_ids=questionnaire_ids,
        repository=repository,
        value=deletion_request.unique_identifier,
    ):
        _device.delete()
        devices.append(_device)
    return devices
