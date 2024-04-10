from itertools import chain

from domain.core.aggregate_root import ExportedEventsTypeDef
from domain.core.device import Device
from domain.core.questionnaire import Questionnaire
from domain.repository.device_repository import DeviceRepository
from sds.domain.constants import ChangeType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs

from .translations import (
    delete_accredited_system_devices,
    delete_mhs_device,
    modify_accredited_system_devices,
    modify_mhs_device,
    nhs_accredited_system_to_cpm_devices,
    nhs_mhs_to_cpm_device,
)

ACCREDITED_SYSTEM_TRANSLATIONS = {
    ChangeType.ADD: nhs_accredited_system_to_cpm_devices,
    ChangeType.MODIFY: modify_accredited_system_devices,
    ChangeType.DELETE: delete_accredited_system_devices,
}

MESSAGE_HANDLING_SYSTEM_TRANSLATIONS = {
    ChangeType.ADD: lambda **kwargs: [nhs_mhs_to_cpm_device(**kwargs)],
    ChangeType.MODIFY: lambda **kwargs: [modify_mhs_device(**kwargs)],
    ChangeType.DELETE: lambda **kwargs: [delete_mhs_device(**kwargs)],
}


def _parse_object_class(object_class: str) -> str:
    for _object_class in (NhsMhs.OBJECT_CLASS, NhsAccreditedSystem.OBJECT_CLASS):
        if object_class.lower() == _object_class:
            return _object_class
    raise NotImplementedError(
        f"No method implemented that translates objects of type '{_object_class}'"
    )


def translate(
    obj: dict[str, str],
    spine_device_questionnaire: Questionnaire,
    _spine_device_questionnaire: dict,
    spine_endpoint_questionnaire: Questionnaire,
    _spine_endpoint_questionnaire: dict,
    repository: DeviceRepository = None,
    _trust=False,
) -> ExportedEventsTypeDef:
    object_class = _parse_object_class(obj["object_class"])

    if object_class == NhsAccreditedSystem.OBJECT_CLASS:
        instance = NhsAccreditedSystem.construct(**obj)
        translate_kwargs = dict(
            nhs_accredited_system=instance,
            questionnaire=spine_device_questionnaire,
            _questionnaire=_spine_device_questionnaire,
            _trust=_trust,
            repository=repository,
        )
        translations = ACCREDITED_SYSTEM_TRANSLATIONS
    else:
        instance = NhsMhs.construct(**obj)
        translate_kwargs = dict(
            nhs_mhs=instance,
            questionnaire=spine_endpoint_questionnaire,
            _questionnaire=_spine_endpoint_questionnaire,
            _trust=_trust,
            repository=repository,
        )
        translations = MESSAGE_HANDLING_SYSTEM_TRANSLATIONS

    devices = translations[instance.change_type](**translate_kwargs)
    return list(chain.from_iterable(map(Device.export_events, devices)))
