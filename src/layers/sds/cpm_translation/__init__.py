from itertools import chain

from domain.core.aggregate_root import ExportedEventsTypeDef
from domain.core.device import Device
from domain.core.questionnaire import Questionnaire
from domain.repository.device_repository import DeviceRepository
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.domain.parse import UnknownSdsModel
from sds.domain.sds_deletion_request import SdsDeletionRequest

from .translations import (
    delete_devices,
    nhs_accredited_system_to_cpm_devices,
    nhs_mhs_to_cpm_device,
)

BAD_UNIQUE_IDENTIFIERS = {
    "31af51067f47f1244d38",  # pragma: allowlist secret
    "a83e1431f26461894465",  # pragma: allowlist secret
    "S2202584A2577603",
    "S100049A300185",
}


def update_in_list_of_dict(obj: list[dict[str, str]], key, value):
    for item in obj:
        if key in item:
            item[key] = value
            return
    obj.append({key: value})


def translate(
    obj: dict[str, str],
    spine_device_questionnaire: Questionnaire,
    _spine_device_questionnaire: dict,
    spine_endpoint_questionnaire: Questionnaire,
    _spine_endpoint_questionnaire: dict,
    repository: DeviceRepository = None,
    _trust=False,
) -> ExportedEventsTypeDef:
    if obj.get("unique_identifier") in BAD_UNIQUE_IDENTIFIERS:
        return []

    object_class = obj["object_class"].lower()
    if object_class == NhsAccreditedSystem.OBJECT_CLASS:
        nhs_accredited_system = NhsAccreditedSystem.construct(**obj)
        devices = nhs_accredited_system_to_cpm_devices(
            nhs_accredited_system=nhs_accredited_system,
            questionnaire=spine_device_questionnaire,
            _questionnaire=_spine_device_questionnaire,
            _trust=_trust,
        )
    elif object_class == NhsMhs.OBJECT_CLASS:
        nhs_mhs = NhsMhs.construct(**obj)
        devices = [
            nhs_mhs_to_cpm_device(
                nhs_mhs=nhs_mhs,
                questionnaire=spine_endpoint_questionnaire,
                _questionnaire=_spine_endpoint_questionnaire,
                _trust=_trust,
            )
        ]
    elif object_class == SdsDeletionRequest.OBJECT_CLASS:
        deletion_request = SdsDeletionRequest.construct(**obj)
        devices = delete_devices(
            deletion_request=deletion_request,
            questionnaire_ids=[
                spine_endpoint_questionnaire.id,
                spine_device_questionnaire.id,
            ],
            repository=repository,
        )
    else:
        raise UnknownSdsModel(
            f"No translation available for models with object class '{object_class}'"
        )

    return list(chain.from_iterable(map(Device.export_events, devices)))
