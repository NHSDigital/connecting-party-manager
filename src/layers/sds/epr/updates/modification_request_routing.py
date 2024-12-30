from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.questionnaire.v1 import Questionnaire
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from sds.domain.constants import ModificationType
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.domain.sds_modification_request import SdsModificationRequest
from sds.epr.updates.change_request_processors import (
    process_request_to_add_to_as,
    process_request_to_add_to_mhs,
    process_request_to_delete_from_as,
    process_request_to_delete_from_mhs,
    process_request_to_replace_in_as,
    process_request_to_replace_in_mhs,
)


def route_mhs_modification_request(
    device: Device,
    cpa_id_to_modify: str,
    request: dict,
    device_reference_data_repository: DeviceReferenceDataRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[Device | DeviceReferenceData]:
    _request = SdsModificationRequest.construct(**request)

    common_payload = dict(
        device=device,
        cpa_id_to_modify=cpa_id_to_modify,
        device_reference_data_repository=device_reference_data_repository,
        mhs_device_questionnaire=mhs_device_questionnaire,
        mhs_device_field_mapping=mhs_device_field_mapping,
        message_set_questionnaire=message_set_questionnaire,
        message_set_field_mapping=message_set_field_mapping,
    )

    domain_objects = []
    for modification_type, ldap_field_name, new_values in _request.modifications:
        field_name = NhsMhs.get_field_name_for_alias(alias=ldap_field_name)
        match modification_type:
            case ModificationType.ADD:
                parsed_value = NhsMhs.parse_and_validate_field(
                    field=field_name, value=new_values
                )
                domain_objects += process_request_to_add_to_mhs(
                    field_name=field_name, new_values=parsed_value, **common_payload
                )
            case ModificationType.REPLACE:
                parsed_value = NhsMhs.parse_and_validate_field(
                    field=field_name, value=new_values
                )
                domain_objects += process_request_to_replace_in_mhs(
                    field_name=field_name,
                    new_values=parsed_value,
                    additional_interactions_questionnaire=additional_interactions_questionnaire,
                    **common_payload,
                )
            case ModificationType.DELETE:
                domain_objects += process_request_to_delete_from_mhs(
                    field_name=field_name, new_values=[], **common_payload
                )
    return domain_objects


def route_as_modification_request(
    device: Device,
    request: dict,
    device_reference_data_repository: DeviceReferenceDataRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[Device | DeviceReferenceData]:
    _request = SdsModificationRequest.construct(**request)

    common_payload = dict(
        device=device,
        device_reference_data_repository=device_reference_data_repository,
        accredited_system_questionnaire=accredited_system_questionnaire,
        accredited_system_field_mapping=accredited_system_field_mapping,
        message_set_questionnaire=message_set_questionnaire,
        message_set_field_mapping=message_set_field_mapping,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
    )

    domain_objects = []
    for modification_type, ldap_field_name, new_values in _request.modifications:
        field_name = NhsAccreditedSystem.get_field_name_for_alias(alias=ldap_field_name)
        match modification_type:
            case ModificationType.ADD:
                parsed_value = NhsAccreditedSystem.parse_and_validate_field(
                    field=field_name, value=new_values
                )
                domain_objects += process_request_to_add_to_as(
                    field_name=field_name, new_values=parsed_value, **common_payload
                )
            case ModificationType.REPLACE:
                parsed_value = NhsAccreditedSystem.parse_and_validate_field(
                    field=field_name, value=new_values
                )
                domain_objects += process_request_to_replace_in_as(
                    field_name=field_name, new_values=parsed_value, **common_payload
                )
            case ModificationType.DELETE:
                domain_objects += process_request_to_delete_from_as(
                    field_name=field_name, **common_payload
                )
    return domain_objects
