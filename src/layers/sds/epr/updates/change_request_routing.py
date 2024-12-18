from typing import Literal

from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.product_team.v1 import ProductTeam
from domain.core.questionnaire import Questionnaire
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository import DeviceRepository
from domain.repository.product_team_repository import ProductTeamRepository
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs
from sds.domain.parse import UnknownSdsModel
from sds.domain.sds_deletion_request import SdsDeletionRequest
from sds.domain.sds_modification_request import SdsModificationRequest
from sds.epr.constants import BAD_UNIQUE_IDENTIFIERS
from sds.epr.updates.change_request_processors import (
    process_request_to_add_as,
    process_request_to_add_mhs,
    process_request_to_delete_as,
    process_request_to_delete_mhs,
)
from sds.epr.updates.etl_device_repository import EtlDeviceRepository
from sds.epr.updates.modification_request_routing import (
    route_as_modification_request,
    route_mhs_modification_request,
)
from sds.epr.utils import is_as_device, is_mhs_device


def process_change_request(
    record: dict[Literal["object_class", "unique_identifier"] | str, str],
    etl_device_repository: EtlDeviceRepository,
    product_team_repository: ProductTeamRepository,
    product_repository: CpmProductRepository,
    device_repository: DeviceRepository,
    device_reference_data_repository: DeviceReferenceDataRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[ProductTeam | CpmProduct | Device | DeviceReferenceData]:
    unique_identifier = record["unique_identifier"]
    if unique_identifier in BAD_UNIQUE_IDENTIFIERS:
        return []

    object_class = record["object_class"].lower()
    if object_class == NhsMhs.OBJECT_CLASS:
        return process_request_to_add_mhs(
            mhs=record,
            product_team_repository=product_team_repository,
            product_repository=product_repository,
            device_repository=device_repository,
            device_reference_data_repository=device_reference_data_repository,
            mhs_device_questionnaire=mhs_device_questionnaire,
            mhs_device_field_mapping=mhs_device_field_mapping,
            message_set_questionnaire=message_set_questionnaire,
            message_set_field_mapping=message_set_field_mapping,
        )
    elif object_class == NhsAccreditedSystem.OBJECT_CLASS:
        return process_request_to_add_as(
            accredited_system=record,
            product_team_repository=product_team_repository,
            product_repository=product_repository,
            device_reference_data_repository=device_reference_data_repository,
            device_repository=device_repository,
            accredited_system_questionnaire=accredited_system_questionnaire,
            accredited_system_field_mapping=accredited_system_field_mapping,
            additional_interactions_questionnaire=additional_interactions_questionnaire,
        )

    device = etl_device_repository.read_if_exists(unique_identifier)
    if device is None:
        return []

    is_deletion_request = object_class == SdsDeletionRequest.OBJECT_CLASS
    is_modification_request = object_class == SdsModificationRequest.OBJECT_CLASS
    is_mhs = is_mhs_device(device)
    is_as = is_as_device(device)

    if is_deletion_request and is_mhs:
        return process_request_to_delete_mhs(
            device=device,
            device_reference_data_repository=device_reference_data_repository,
            message_set_questionnaire=message_set_questionnaire,
            message_set_field_mapping=message_set_field_mapping,
        )
    elif is_deletion_request and is_as:
        return process_request_to_delete_as(
            device=device,
            device_reference_data_repository=device_reference_data_repository,
            additional_interactions_questionnaire=additional_interactions_questionnaire,
        )
    elif is_modification_request and is_mhs:
        return route_mhs_modification_request(
            device=device,
            request=record,
            device_reference_data_repository=device_reference_data_repository,
            mhs_device_questionnaire=mhs_device_questionnaire,
            mhs_device_field_mapping=mhs_device_field_mapping,
            message_set_questionnaire=message_set_questionnaire,
            message_set_field_mapping=message_set_field_mapping,
            additional_interactions_questionnaire=additional_interactions_questionnaire,
        )
    elif is_modification_request and is_as:
        return route_as_modification_request(
            device=device,
            request=record,
            device_reference_data_repository=device_reference_data_repository,
            accredited_system_questionnaire=accredited_system_questionnaire,
            accredited_system_field_mapping=accredited_system_field_mapping,
            message_set_questionnaire=message_set_questionnaire,
            message_set_field_mapping=message_set_field_mapping,
            additional_interactions_questionnaire=additional_interactions_questionnaire,
        )

    raise UnknownSdsModel(
        f"No translation available for models with object class '{object_class}'"
    )
