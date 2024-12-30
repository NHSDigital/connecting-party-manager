from collections.abc import Callable
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_key.v1 import DeviceKey, DeviceKeyType
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.error import ImmutableFieldError
from domain.core.product_team.v1 import ProductTeam
from domain.core.questionnaire.v1 import Questionnaire, QuestionnaireResponse
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from sds.epr.constants import SdsDeviceReferenceDataPath
from sds.epr.constants import CPM_MHS_IMMUTABLE_FIELDS, SdsDeviceReferenceDataPath
from sds.epr.getters import (
    get_message_set_data,
    get_mhs_device_data,
    get_accredited_system_device_data,
    get_accredited_system_tags,
)

from sds.epr.readers import (
    read_additional_interactions_if_exists,
    read_or_create_as_device,
    read_or_create_empty_additional_interactions,
    read_message_sets_from_mhs_device,
    read_or_create_empty_message_sets,
    read_or_create_epr_product,
    read_or_create_epr_product_team,
    read_or_create_mhs_device,
)
from sds.epr.updaters import (
    UnexpectedModification,
    ldif_add_to_field_in_questionnaire,
    remove_erroneous_additional_interactions,
    update_message_sets,
    update_new_additional_interactions,
)
from sds.epr.updates.etl_device import EtlDevice
from sds.epr.utils import filter_message_set_by_cpa_id


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
    device_repository: DeviceRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[ProductTeam, CpmProduct, DeviceReferenceData, Device]:
    asid = accredited_system["unique_identifier"]
    product_name = accredited_system["nhs_product_name"] or asid
    party_key = accredited_system["nhs_mhs_party_key"]
    ods_code = accredited_system["nhs_mhs_manufacturer_org"]

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

    message_sets = read_or_create_empty_message_sets(
        product=product,
        party_key=party_key,
        device_reference_data_repository=device_reference_data_repository,
    )

    additional_interactions = read_or_create_empty_additional_interactions(
        product=product,
        party_key=party_key,
        device_reference_data_repository=device_reference_data_repository,
    )
    additional_interactions = update_new_additional_interactions(
        incoming_accredited_system_interactions=accredited_system["nhs_as_svc_ia"],
        additional_interactions=additional_interactions,
        message_sets=message_sets,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
    )

    accredited_system_device_data = get_accredited_system_device_data(
        accredited_system=accredited_system,
        accredited_system_questionnaire=accredited_system_questionnaire,
        accredited_system_field_mapping=accredited_system_field_mapping,
    )
    as_tags = get_accredited_system_tags(accredited_system)

    accredited_system_device = read_or_create_as_device(
        device_repository=device_repository,
        asid=asid,
        party_key=party_key,
        product_team=product_team,
        product=product,
        message_sets=message_sets,
        additional_interactions=additional_interactions,
        accredited_system_device_data=accredited_system_device_data,
        as_tags=as_tags,
    )

    asid_key = DeviceKey(key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value=asid)
    if asid_key not in accredited_system_device.keys:
        accredited_system_device.add_key(**asid_key.dict())

    if str(message_sets.id) not in accredited_system_device.device_reference_data:
        accredited_system_device.add_device_reference_data_id(
            message_sets.id,
            path_to_data=[SdsDeviceReferenceDataPath.ALL_INTERACTION_IDS],
        )
    if (
        str(additional_interactions.id)
        not in accredited_system_device.device_reference_data
    ):
        accredited_system_device.add_device_reference_data_id(
            additional_interactions.id,
            path_to_data=[SdsDeviceReferenceDataPath.ALL_INTERACTION_IDS],
        )

    return [
        product_team,
        product,
        message_sets,
        additional_interactions,
        accredited_system_device,
    ]


def process_request_to_delete_mhs(
    device: Device,
    cpa_id_to_delete: str,
    device_reference_data_repository: DeviceReferenceDataRepository,
) -> list[EtlDevice | DeviceReferenceData]:
    """
    * MHS Device has been passed in by CPA ID
    * Deletes the Message Sets Questionnaire Response that corresponds to this CPA ID
    * Deletes the Device key corresponding to the CPA ID
    * If no more keys left in this Device then hard delete the Device
    """
    etl_device = EtlDevice(**device.state())
    etl_device.delete_key(key_type=DeviceKeyType.CPA_ID, key_value=cpa_id_to_delete)

    message_sets = read_message_sets_from_mhs_device(
        device_reference_data_repository=device_reference_data_repository,
        mhs_device=device,
    )
    message_set_to_delete = filter_message_set_by_cpa_id(
        cpa_id=cpa_id_to_delete, message_sets=message_sets
    )
    message_sets.remove_questionnaire_response(
        questionnaire_id=message_set_to_delete.questionnaire_id,
        questionnaire_response_id=message_set_to_delete.id,
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


def _process_request_to_modify_mhs(
    device: Device,
    cpa_id_to_modify: str,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict[str, str],
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict[str, str],
    ldif_modify_field_in_questionnaire: Callable[
        [
            str,
            set[str],
            dict,
            Questionnaire,
        ],
        QuestionnaireResponse,
    ],
) -> list[Device | DeviceReferenceData]:
    """
    * MHS Device has been passed in by CPA ID
    * Updates EITHER:
    ** the MHS Device Questionnaire Response, OR
    ** the Message Sets Questionnaire Response that corresponds to this CPA ID
    * If the modified field is an interaction ID, then fix-up the Additional Interactions
      Questionnaire Responses as well
    """
    message_set_field = message_set_field_mapping.get(field_name)
    mhs_device_field = mhs_device_field_mapping.get(field_name)
    translated_field: str = message_set_field or mhs_device_field

    if translated_field in CPM_MHS_IMMUTABLE_FIELDS:
        raise ImmutableFieldError(
            f"'{field_name}' is an immutable MHS field in the context of EPR in CPM"
        )

    # Read and filter inputs
    ((device_questionnaire_to_modify,),) = device.questionnaire_responses.values()
    message_sets = read_message_sets_from_mhs_device(
        device_reference_data_repository=device_reference_data_repository,
        mhs_device=device,
    )
    message_set_to_modify = filter_message_set_by_cpa_id(
        cpa_id=cpa_id_to_modify, message_sets=message_sets
    )

    # Determine which objects need to be modified
    modify_message_sets = message_set_field and not mhs_device_field
    modify_mhs_device = mhs_device_field and not message_set_field

    # Route the operation
    if modify_message_sets:
        updated_questionnaire_response = ldif_modify_field_in_questionnaire(
            field_name=translated_field,
            new_values=new_values,
            current_data=message_set_to_modify.data,
            questionnaire=message_set_questionnaire,
        )
        message_sets.remove_questionnaire_response(
            questionnaire_id=message_set_to_modify.questionnaire_id,
            questionnaire_response_id=message_set_to_modify.id,
        )
        message_sets.add_questionnaire_response(
            questionnaire_response=updated_questionnaire_response
        )
    elif modify_mhs_device:
        updated_questionnaire_response = ldif_modify_field_in_questionnaire(
            field_name=translated_field,
            new_values=new_values,
            current_data=device_questionnaire_to_modify.data,
            questionnaire=mhs_device_questionnaire,
        )
        device.remove_questionnaire_response(
            questionnaire_id=device_questionnaire_to_modify.questionnaire_id,
            questionnaire_response_id=device_questionnaire_to_modify.id,
        )
        device.add_questionnaire_response(
            questionnaire_response=updated_questionnaire_response
        )

    else:
        # Should not be reachable, but better to bail to avoid unexpected side-effects
        raise UnexpectedModification(
            f"No strategy implemented for field name '{field_name}' given "
            f"MHS Device fields {list(mhs_device_field_mapping.keys())} and "
            f"Message Set fields {list(message_set_field_mapping.keys())}"
        )

    return [device, message_sets]


def process_request_to_add_to_mhs(
    device: Device,
    cpa_id_to_modify: str,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
) -> list[Device | DeviceReferenceData]:
    return _process_request_to_modify_mhs(
        device=device,
        cpa_id_to_modify=cpa_id_to_modify,
        field_name=field_name,
        new_values=new_values,
        device_reference_data_repository=device_reference_data_repository,
        mhs_device_questionnaire=mhs_device_questionnaire,
        mhs_device_field_mapping=mhs_device_field_mapping,
        message_set_questionnaire=message_set_questionnaire,
        message_set_field_mapping=message_set_field_mapping,
        ldif_modify_field_in_questionnaire=ldif_add_to_field_in_questionnaire,
    )


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
    cpa_id_to_modify: str,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
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
