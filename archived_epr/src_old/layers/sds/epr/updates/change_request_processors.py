from collections.abc import Callable

from domain.api.sds.query import SearchSDSDeviceQueryParams
from domain.core.device.v1 import Device
from domain.core.device_key.v1 import DeviceKey, DeviceKeyType
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.enum import Environment
from domain.core.epr_product.v1 import EprProduct
from domain.core.error import ImmutableFieldError
from domain.core.product_team_epr.v1 import ProductTeam
from domain.core.questionnaire.v1 import Questionnaire, QuestionnaireResponse
from domain.repository.device_reference_data_repository.v1 import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository.v1 import DeviceRepository
from domain.repository.epr_product_repository.v1 import EprProductRepository
from domain.repository.product_team_epr_repository.v1 import ProductTeamRepository
from sds.domain.constants import ModificationType
from sds.epr.constants import (
    CPM_ACCREDITED_SYSTEM_IMMUTABLE_FIELDS,
    CPM_MHS_IMMUTABLE_FIELDS,
    SdsDeviceReferenceDataPath,
)
from sds.epr.getters import (
    get_accredited_system_device_data,
    get_accredited_system_tags,
    get_message_set_data,
    get_mhs_device_data,
)
from sds.epr.readers import (
    read_additional_interactions_if_exists,
    read_drds_from_as_device,
    read_message_sets_from_mhs_device,
    read_or_create_as_device,
    read_or_create_empty_additional_interactions,
    read_or_create_empty_message_sets,
    read_or_create_epr_product,
    read_or_create_epr_product_team,
    read_or_create_mhs_device,
)
from sds.epr.tags import sds_metadata_to_device_tags
from sds.epr.updaters import (
    UnexpectedModification,
    ldif_add_to_field_in_questionnaire,
    ldif_modify_field_in_questionnaire,
    ldif_remove_field_from_questionnaire,
    remove_erroneous_additional_interactions,
    update_message_sets,
    update_new_additional_interactions,
)
from sds.epr.updates.etl_device import EtlDevice
from sds.epr.utils import (
    filter_message_set_by_cpa_id,
    get_interaction_ids,
    is_as_device,
)


def process_request_to_add_mhs(
    mhs: dict,
    product_team_repository: ProductTeamRepository,
    product_repository: EprProductRepository,
    device_reference_data_repository: DeviceReferenceDataRepository,
    device_repository: DeviceRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
) -> list[ProductTeam, EprProduct, DeviceReferenceData, DeviceReferenceData, Device]:
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
    product_repository: EprProductRepository,
    device_reference_data_repository: DeviceReferenceDataRepository,
    device_repository: DeviceRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
) -> list[ProductTeam, EprProduct, DeviceReferenceData, Device]:
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
    additional_interactions, new_additional_interactions = (
        update_new_additional_interactions(
            incoming_accredited_system_interactions=accredited_system["nhs_as_svc_ia"],
            additional_interactions=additional_interactions,
            message_sets=message_sets,
            additional_interactions_questionnaire=additional_interactions_questionnaire,
        )
    )

    # Update any existing AS devices with new interactions
    updated_existing_as_devices = []
    if new_additional_interactions:
        devices = device_repository.search(
            product_team_id=product_team.id,
            product_id=product.id,
            environment=Environment.PROD,
        )
        as_devices = list(filter(is_as_device, devices))
        if as_devices:
            # Construct all new tags upfront
            new_tags = []
            for new_interaction in new_additional_interactions:
                data = {
                    "nhs_as_svc_ia": new_interaction,
                    "nhs_id_code": ods_code,
                    "nhs_mhs_party_key": party_key,
                }
                _new_tags = sds_metadata_to_device_tags(
                    data=data, model=SearchSDSDeviceQueryParams
                )
                new_tags_to_append = [dict(tag) for tag in set(_new_tags)]
                new_tags.extend(new_tags_to_append)

            for device in as_devices:
                device.add_tags(new_tags)
                updated_existing_as_devices.append(device)

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
        *updated_existing_as_devices,
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
) -> list[EtlDevice, DeviceReferenceData]:
    """
    * AS Device has been passed in by ASID
    * Hard deletes the AS Device, using the EtlDevice wrapper
    * If no more AS Devices in this product then also clears all
      questionnaire responses from the AS DRD
    """
    etl_device = EtlDevice(**device.state())
    etl_device.hard_delete()

    devices = device_repository.search(
        product_team_id=device.product_team_id,
        product_id=device.product_id,
        environment=Environment.PROD,
    )
    additional_interactions = read_additional_interactions_if_exists(
        device_reference_data_repository=device_reference_data_repository,
        product_team_id=device.product_team_id,
        product_id=device.product_id,
    )

    other_as_devices_in_this_product = (
        d for d in filter(is_as_device, devices) if d.id != device.id
    )
    if not any(other_as_devices_in_this_product):
        (questionnaire_id,) = additional_interactions.questionnaire_responses.keys()
        additional_interactions.clear_questionnaire_responses(
            questionnaire_id=questionnaire_id
        )

    return [etl_device, additional_interactions]


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
    cpa_id_to_modify: str,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
) -> list[Device | DeviceReferenceData]:
    mhs_device, message_sets = _process_request_to_modify_mhs(
        device=device,
        cpa_id_to_modify=cpa_id_to_modify,
        field_name=field_name,
        new_values=new_values,
        device_reference_data_repository=device_reference_data_repository,
        mhs_device_questionnaire=mhs_device_questionnaire,
        mhs_device_field_mapping=mhs_device_field_mapping,
        message_set_questionnaire=message_set_questionnaire,
        message_set_field_mapping=message_set_field_mapping,
        ldif_modify_field_in_questionnaire=ldif_modify_field_in_questionnaire,
    )

    additional_interactions = read_additional_interactions_if_exists(
        device_reference_data_repository=device_reference_data_repository,
        product_team_id=mhs_device.product_team_id,
        product_id=mhs_device.product_id,
    )
    if additional_interactions:
        additional_interactions = remove_erroneous_additional_interactions(
            message_sets=message_sets, additional_interactions=additional_interactions
        )
    return [mhs_device, message_sets, additional_interactions]


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
        ldif_modify_field_in_questionnaire=ldif_remove_field_from_questionnaire,
    )


def _process_request_to_modify_as(
    modification_type: str,
    device: Device,
    device_repository: DeviceRepository,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
    additional_interactions_field_mapping: dict,
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
    * AS Device has been passed in by ASID
    * Updates EITHER:
    ** the AS Device Questionnaire Response, OR
    ** the Additional Interactions Questionnaire Response
    * If the modified field is an interaction ID, then only update the Additional Interactions
      Questionnaire Response if the interaction isn't presnt in the Message Set response
      In this case add as a tag to the device and all other AS devices in that product
    """
    additional_interactions_field = additional_interactions_field_mapping.get(
        field_name
    )
    as_device_field = accredited_system_field_mapping.get(field_name)
    translated_field: str = additional_interactions_field or as_device_field

    if translated_field in CPM_ACCREDITED_SYSTEM_IMMUTABLE_FIELDS:
        raise ImmutableFieldError(
            f"'{field_name}' is an immutable MHS field in the context of EPR in CPM"
        )

    # Read and filter inputs
    ((device_questionnaire_to_modify,),) = device.questionnaire_responses.values()
    message_sets, additional_interactions = read_drds_from_as_device(
        as_device=device,
        device_reference_data_repository=device_reference_data_repository,
    )
    additional_interactions_interaction_ids = get_interaction_ids(
        additional_interactions
    )
    message_sets_interaction_ids = get_interaction_ids(message_sets)

    # Determine which objects need to be modified
    modify_additional_interactions = (
        additional_interactions_field and not as_device_field
    )
    modify_as_device = as_device_field and not additional_interactions_field

    updated_existing_as_devices = []
    # Route the operation
    if modify_additional_interactions:
        # Check if Interaction ID field is being deleted
        if modification_type == ModificationType.DELETE:
            raise UnexpectedModification(f"Cannot remove required field '{field_name}'")

        # Get Party Key
        spine_as_responses = device.questionnaire_responses.get("spine_as/1", [])
        party_key = spine_as_responses[0].data.get("MHS Party Key")
        # Get all devices that may need updating
        product_team_id = device.product_team_id
        product_id = device.product_id
        devices = device_repository.search(
            product_team_id=product_team_id,
            product_id=product_id,
            environment=Environment.PROD,
        )
        as_devices = list(filter(is_as_device, devices))

        if modification_type == ModificationType.ADD:
            new_tags = []
            # Check each new value is not present in message set or additional interactions already
            for new_value in new_values:
                if (
                    new_value not in additional_interactions_interaction_ids
                    and new_value not in message_sets_interaction_ids
                ):
                    # Add a new additional interactions response for the new value
                    new_questionnaire_response = ldif_modify_field_in_questionnaire(
                        field_name=translated_field,
                        new_values=[new_value],
                        current_data={},
                        questionnaire=additional_interactions_questionnaire,
                    )
                    additional_interactions.add_questionnaire_response(
                        questionnaire_response=new_questionnaire_response
                    )
                    # Construct new tag data
                    data = {
                        "nhs_as_svc_ia": new_value,
                        "nhs_id_code": device.ods_code,
                        "nhs_mhs_party_key": party_key,
                    }
                    _new_tags = sds_metadata_to_device_tags(
                        data=data, model=SearchSDSDeviceQueryParams
                    )
                    new_tags_to_append = [dict(tag) for tag in set(_new_tags)]
                    new_tags.extend(new_tags_to_append)
                    # Update tags on ALL AS devices under the product
            for device in as_devices:
                if new_tags:
                    device.add_tags(new_tags)
                    updated_existing_as_devices.append(device)

        if modification_type == ModificationType.REPLACE:
            new_tags = []
            # Remove all existing additional interactions questionnaire responses
            (questionnaire_id,) = additional_interactions.questionnaire_responses.keys()
            additional_interactions.clear_questionnaire_responses(
                questionnaire_id=questionnaire_id
            )
            # Remove existing tags from all AS devices under the product
            for device in as_devices:
                device.clear_tags()

            # Update device tags and additional interaction responses for each new value
            for new_value in new_values:
                data = {
                    "nhs_as_svc_ia": new_value,
                    "nhs_id_code": device.ods_code,
                    "nhs_mhs_party_key": party_key,
                }
                _new_tags = sds_metadata_to_device_tags(
                    data=data, model=SearchSDSDeviceQueryParams
                )
                new_tags_to_append = [dict(tag) for tag in set(_new_tags)]
                new_tags.extend(new_tags_to_append)

                if new_value not in message_sets_interaction_ids:
                    # Add additional interactions questionnaire response
                    new_questionnaire_response = ldif_modify_field_in_questionnaire(
                        field_name=translated_field,
                        new_values=[new_value],
                        current_data={},
                        questionnaire=additional_interactions_questionnaire,
                    )
                    additional_interactions.add_questionnaire_response(
                        questionnaire_response=new_questionnaire_response
                    )
            for device in as_devices:
                device.add_tags(new_tags)
                updated_existing_as_devices.append(device)

        # If modifying additional interactions, return updated devices and interactions.
        # This avoids duplicates as 'device' will be part of the updated list.
        return [
            additional_interactions,
            *updated_existing_as_devices,
        ]

    elif modify_as_device:
        new_questionnaire_response = ldif_modify_field_in_questionnaire(
            field_name=translated_field,
            new_values=new_values,
            current_data=device_questionnaire_to_modify.data,
            questionnaire=accredited_system_questionnaire,
        )
        device.remove_questionnaire_response(
            questionnaire_id=device_questionnaire_to_modify.questionnaire_id,
            questionnaire_response_id=device_questionnaire_to_modify.id,
        )
        device.add_questionnaire_response(
            questionnaire_response=new_questionnaire_response
        )

        return [
            device,
            additional_interactions,
        ]

    else:
        # Should not be reachable, but better to bail to avoid unexpected side-effects
        raise UnexpectedModification(
            f"No strategy implemented for field name '{field_name}' given "
            f"AS Device fields {list(accredited_system_field_mapping.keys())} and "
            f"Additional Interactions fields {list(additional_interactions_field_mapping.keys())}"
        )


def process_request_to_add_to_as(
    device: Device,
    device_repository: DeviceRepository,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
    additional_interactions_field_mapping: dict,
) -> list[Device | DeviceReferenceData]:
    return _process_request_to_modify_as(
        modification_type=ModificationType.ADD,
        device=device,
        device_repository=device_repository,
        field_name=field_name,
        new_values=new_values,
        device_reference_data_repository=device_reference_data_repository,
        accredited_system_questionnaire=accredited_system_questionnaire,
        accredited_system_field_mapping=accredited_system_field_mapping,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
        additional_interactions_field_mapping=additional_interactions_field_mapping,
        ldif_modify_field_in_questionnaire=ldif_add_to_field_in_questionnaire,
    )


def process_request_to_replace_in_as(
    device: Device,
    device_repository: DeviceRepository,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
    additional_interactions_field_mapping: dict,
) -> list[Device, DeviceReferenceData]:
    return _process_request_to_modify_as(
        modification_type=ModificationType.REPLACE,
        device=device,
        device_repository=device_repository,
        field_name=field_name,
        new_values=new_values,
        device_reference_data_repository=device_reference_data_repository,
        accredited_system_questionnaire=accredited_system_questionnaire,
        accredited_system_field_mapping=accredited_system_field_mapping,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
        additional_interactions_field_mapping=additional_interactions_field_mapping,
        ldif_modify_field_in_questionnaire=ldif_modify_field_in_questionnaire,
    )


def process_request_to_delete_from_as(
    device: Device,
    device_repository: DeviceRepository,
    field_name: str,
    new_values: set[str],
    device_reference_data_repository: DeviceReferenceDataRepository,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
    additional_interactions_field_mapping: dict,
) -> list[Device | DeviceReferenceData]:
    return _process_request_to_modify_as(
        modification_type=ModificationType.DELETE,
        device=device,
        device_repository=device_repository,
        field_name=field_name,
        new_values=new_values,
        device_reference_data_repository=device_reference_data_repository,
        accredited_system_questionnaire=accredited_system_questionnaire,
        accredited_system_field_mapping=accredited_system_field_mapping,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
        additional_interactions_field_mapping=additional_interactions_field_mapping,
        ldif_modify_field_in_questionnaire=ldif_remove_field_from_questionnaire,
    )
