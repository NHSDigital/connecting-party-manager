from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_key.v1 import DeviceKey, DeviceKeyType
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.enum import Environment
from domain.core.product_team.v1 import ProductTeam
from domain.core.questionnaire.v1 import Questionnaire
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from sds.epr.constants import SdsDeviceReferenceDataPath, SdsFieldName
from sds.epr.getters import get_message_set_data, get_mhs_device_data
from sds.epr.readers import (
    read_additional_interactions_if_exists,
    read_or_create_empty_message_sets,
    read_or_create_epr_product,
    read_or_create_epr_product_team,
    read_or_create_mhs_device,
)
from sds.epr.updaters import (
    remove_erroneous_additional_interactions,
    update_message_sets,
)
from sds.epr.updates.etl_device import EtlDevice


def process_request_to_add_mhs(
    mhs: dict,
    product_team_repository: ProductTeamRepository,
    product_repository: CpmProductRepository,
    device_reference_data_repository: DeviceReferenceDataRepository,
    device_repository: DeviceRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
) -> list[ProductTeam, CpmProduct, DeviceReferenceData, DeviceReferenceData, Device]:
    cpa_id = mhs["nhs_mhs_cpa_id"]
    product_name = mhs["nhs_product_name"] or cpa_id
    party_key = mhs["nhs_mhs_party_key"]
    ods_code = mhs["nhs_mhs_manufacturer_org"]

    product_team = read_or_create_epr_product_team(
        ods_code=ods_code,
        product_team_repository=product_team_repository,
    )
    product = read_or_create_epr_product(
        product_team=product_team,
        product_name=product_name,
        party_key=party_key,
        product_repository=product_repository,
    )

    message_set_data = get_message_set_data(
        [mhs],
        message_set_questionnaire=message_set_questionnaire,
        message_set_field_mapping=message_set_field_mapping,
    )
    message_sets = read_or_create_empty_message_sets(
        product=product,
        party_key=party_key,
        device_reference_data_repository=device_reference_data_repository,
    )
    message_sets = update_message_sets(
        message_sets=message_sets, message_set_data=message_set_data
    )

    mhs_device_data = get_mhs_device_data(
        mhs=mhs,
        mhs_device_questionnaire=mhs_device_questionnaire,
        mhs_device_field_mapping=mhs_device_field_mapping,
    )

    additional_interactions = read_additional_interactions_if_exists(
        device_reference_data_repository=device_reference_data_repository,
        product_team_id=product.product_team_id,
        product_id=product.id,
    )
    if additional_interactions:
        additional_interactions = remove_erroneous_additional_interactions(
            message_sets=message_sets, additional_interactions=additional_interactions
        )

    mhs_device = read_or_create_mhs_device(
        device_repository=device_repository,
        cpa_id=cpa_id,
        party_key=party_key,
        product_team=product_team,
        product=product,
        message_sets=message_sets,
        mhs_device_data=mhs_device_data,
    )

    cpa_id_key = DeviceKey(key_type=DeviceKeyType.CPA_ID, key_value=cpa_id)
    if cpa_id_key not in mhs_device.keys:
        mhs_device.add_key(**cpa_id_key.dict())

    if str(message_sets.id) not in mhs_device.device_reference_data:
        mhs_device.add_device_reference_data_id(
            message_sets.id, path_to_data=[SdsDeviceReferenceDataPath.ALL]
        )

    return [product_team, product, message_sets, additional_interactions, mhs_device]


def process_request_to_add_as(
    accredited_system: dict,
    product_team_repository: ProductTeamRepository,
    product_repository: CpmProductRepository,
    device_reference_data_repository: DeviceReferenceDataRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[ProductTeam, CpmProduct, DeviceReferenceData, Device]:
    raise NotImplementedError()


def process_request_to_delete_mhs(
    device: Device,
    cpa_id_to_delete: str,
    device_reference_data_repository: DeviceReferenceDataRepository,
) -> list[EtlDevice | DeviceReferenceData]:
    """
    * MHS Device has been passed in by CPA ID
    * Deletes the Questionnaire Response that corresponds to this CPA ID
    * Deletes the Device key corresponding to the CPA ID
    * If no more keys left in this Device then hard delete the Device
    """
    etl_device = EtlDevice(**device.state())

    (message_sets_id,) = device.device_reference_data.keys()
    message_sets = device_reference_data_repository.read(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        id=message_sets_id,
        environment=Environment.PROD,
    )
    (message_sets_questionnaire_id,) = message_sets.questionnaire_responses.keys()
    (message_set_id_to_delete,) = {
        qr.id
        for qr in message_sets.questionnaire_responses[message_sets_questionnaire_id]
        if qr.data[SdsFieldName.CPA_ID] == cpa_id_to_delete
    }

    etl_device.delete_key(key_type=DeviceKeyType.CPA_ID, key_value=cpa_id_to_delete)
    message_sets.remove_questionnaire_response(
        questionnaire_id=message_sets_questionnaire_id,
        questionnaire_response_id=message_set_id_to_delete,
    )
    if len(etl_device.keys) == 0:
        etl_device.hard_delete()
    return [etl_device, message_sets]


def process_request_to_delete_as(
    device: Device,
    device_repository: DeviceRepository,
    device_reference_data_repository: DeviceReferenceDataRepository,
    additional_interactions_questionnaire: Questionnaire,
) -> list[Device, DeviceReferenceData]:
    raise NotImplementedError()


def process_request_to_add_to_mhs(
    device: Device,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[Device, DeviceReferenceData, DeviceReferenceData]:
    raise NotImplementedError()


def process_request_to_replace_in_mhs(
    device: Device,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[Device, DeviceReferenceData, DeviceReferenceData]:
    raise NotImplementedError()


def process_request_to_delete_from_mhs(
    device: Device,
    field_name: str,
    device_reference_data_repository: DeviceReferenceDataRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[Device, DeviceReferenceData, DeviceReferenceData]:
    raise NotImplementedError()


def process_request_to_add_to_as(
    device: Device,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[Device, DeviceReferenceData]:
    raise NotImplementedError()


def process_request_to_replace_in_as(
    device: Device,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[Device, DeviceReferenceData]:
    raise NotImplementedError()


def process_request_to_delete_from_as(
    device: Device,
    field_name: str,
    device_reference_data_repository: DeviceReferenceDataRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[Device, DeviceReferenceData]:
    raise NotImplementedError()
