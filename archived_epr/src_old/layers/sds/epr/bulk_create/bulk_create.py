from typing import Literal

from domain.core.aggregate_root import AggregateRoot
from domain.core.product_team_epr.v1 import ProductTeam
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from sds.domain.nhs_mhs import NhsMhs
from sds.epr.constants import SdsFieldName
from sds.epr.creators import (
    create_additional_interactions,
    create_as_device,
    create_epr_product,
    create_epr_product_team,
    create_message_sets,
    create_mhs_device,
)
from sds.epr.getters import (
    get_accredited_system_device_data,
    get_accredited_system_tags,
    get_additional_interactions_data,
    get_message_set_data,
    get_mhs_device_data,
    get_mhs_tags,
)


def _create_complete_epr_product(
    ods_code: str,
    party_key: str,
    product_name: str,
    mhs_device_data: QuestionnaireResponse,
    message_set_data: list[QuestionnaireResponse],
    mhs_cpa_ids: list[str],
    mhs_tags: list[dict],
    additional_interactions_data: list[QuestionnaireResponse],
    as_device_data: list[QuestionnaireResponse],
    as_tags: list[list[dict]],
    product_team_ids: dict[str, str],
) -> list[AggregateRoot]:
    if ods_code in product_team_ids:
        product_team = ProductTeam(
            name="placeholder", id=product_team_ids[ods_code], ods_code=ods_code
        )
        product_teams_to_create = []
    else:
        product_team = create_epr_product_team(ods_code=ods_code)
        product_team_ids[ods_code] = product_team.id
        product_teams_to_create = [product_team]

    product = create_epr_product(
        product_team=product_team, product_name=product_name, party_key=party_key
    )
    message_sets = create_message_sets(
        product=product, party_key=party_key, message_set_data=message_set_data
    )

    mhs_devices = []
    if mhs_device_data:
        mhs_device = create_mhs_device(
            product=product,
            party_key=party_key,
            mhs_device_data=mhs_device_data,
            cpa_ids=mhs_cpa_ids,
            message_sets_id=message_sets.id,
        )
        mhs_devices = [mhs_device]

    additional_interactions = create_additional_interactions(
        product=product,
        party_key=party_key,
        additional_interactions_data=additional_interactions_data,
    )
    as_devices = [
        create_as_device(
            product=product,
            party_key=party_key,
            asid=data.data[SdsFieldName.ASID],
            as_device_data=data,
            additional_interactions_id=additional_interactions.id,
            message_sets_id=message_sets.id,
            as_tags=tags,
        )
        for data, tags in zip(as_device_data, as_tags)
    ]

    return [
        *product_teams_to_create,
        product,
        message_sets,
        additional_interactions,
        *mhs_devices,
        *as_devices,
    ]


def _impute_manufacturer_org(
    item: dict[Literal["nhs_mhs_manufacturer_org", "nhs_id_code"], str]
):
    """
    Impute nhs_mhs_manufacturer_org if it is clearly invalid (not alphanumeric)
    or does not exist by replacing it with the nhs_id_code
    """
    manufacturer_org = item["nhs_mhs_manufacturer_org"]
    item["nhs_mhs_manufacturer_org"] = (
        manufacturer_org
        if manufacturer_org is not None and manufacturer_org.isalnum()
        else item["nhs_id_code"]
    )
    return item


def create_complete_epr_product(
    party_key_group: list[dict],
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
    additional_interactions_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
    accredited_system_questionnaire: Questionnaire,
    product_team_ids: dict[str, str],
):
    """
    NB: For this to work we will need to have a specific apply_action
    for extract-bulk which buffers objects into party key groups, in the form
    deque[list[MHS | AS]]
    """
    message_handling_systems: list[dict] = []
    accredited_systems: list[dict] = []
    for item in party_key_group:
        item = _impute_manufacturer_org(item)
        if item["object_class"].lower() == NhsMhs.OBJECT_CLASS:
            message_handling_systems.append(item)
        else:
            accredited_systems.append(item)

    # !! Assumption: All MHSs with this party key have the same basic metadata.
    # !! Could add a debug test here to ensure all of this metadata is equal
    # !! between MHSs with this party key.
    ods_code, party_key, product_name = None, None, None
    mhs_device_data = None
    if message_handling_systems:
        first_mhs = message_handling_systems[0]
        mhs_device_data = get_mhs_device_data(
            mhs=first_mhs,
            mhs_device_questionnaire=mhs_device_questionnaire,
            mhs_device_field_mapping=mhs_device_field_mapping,
        )
        ods_code = first_mhs["nhs_mhs_manufacturer_org"]
        party_key = first_mhs["nhs_mhs_party_key"]
        product_name = first_mhs["nhs_product_name"] or first_mhs["nhs_mhs_cpa_id"]
    else:
        first_as = accredited_systems[0]
        ods_code = first_as["nhs_mhs_manufacturer_org"]
        party_key = first_as["nhs_mhs_party_key"]
        product_name = first_as["nhs_product_name"]

    as_device_data = [
        get_accredited_system_device_data(
            accredited_system=accredited_system,
            accredited_system_questionnaire=accredited_system_questionnaire,
            accredited_system_field_mapping=accredited_system_field_mapping,
        )
        for accredited_system in accredited_systems
    ]

    message_set_data = get_message_set_data(
        message_handling_systems=message_handling_systems,
        message_set_questionnaire=message_set_questionnaire,
        message_set_field_mapping=message_set_field_mapping,
    )
    additional_interactions_data = get_additional_interactions_data(
        accredited_systems=accredited_systems,
        additional_interactions_questionnaire=additional_interactions_questionnaire,
    )

    mhs_tags = get_mhs_tags(message_handling_systems)
    as_tags = [
        get_accredited_system_tags(accredited_system)
        for accredited_system in accredited_systems
    ]

    return _create_complete_epr_product(
        ods_code=ods_code,
        party_key=party_key,
        product_name=product_name,
        mhs_device_data=mhs_device_data,
        message_set_data=message_set_data,
        mhs_cpa_ids=[mhs["unique_identifier"] for mhs in message_handling_systems],
        mhs_tags=mhs_tags,
        additional_interactions_data=additional_interactions_data,
        as_device_data=as_device_data,
        as_tags=as_tags,
        product_team_ids=product_team_ids,
    )
