from domain.core.cpm_product import CpmProduct
from domain.core.device import Device
from domain.core.device_key import DeviceKeyType
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.enum import Environment
from domain.core.product_key import ProductKeyType
from domain.core.product_team_epr import ProductTeam
from domain.core.product_team_key import ProductTeamKey, ProductTeamKeyType
from domain.core.questionnaire import QuestionnaireResponse
from domain.core.root import Root
from sds.epr.constants import (
    EXCEPTIONAL_ODS_CODES,
    EprNameTemplate,
    SdsDeviceReferenceDataPath,
)


def create_epr_product_team(ods_code: str) -> ProductTeam:
    product_team_key = ProductTeamKey(
        key_type=ProductTeamKeyType.EPR_ID,
        key_value=EprNameTemplate.PRODUCT_TEAM_KEY.format(ods_code=ods_code),
    )
    org = Root.create_ods_organisation(ods_code=ods_code)

    if ods_code in EXCEPTIONAL_ODS_CODES:
        return ProductTeam(
            name=EprNameTemplate.PRODUCT_TEAM.format(ods_code=ods_code),
            ods_code=ods_code,
            keys=[product_team_key],
        )
    return org.create_product_team_epr(
        name=EprNameTemplate.PRODUCT_TEAM.format(ods_code=ods_code),
        keys=[product_team_key],
    )


def create_epr_product(
    product_team: ProductTeam, product_name: str, party_key: str
) -> CpmProduct:
    product = product_team.create_cpm_product(name=product_name)
    product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value=party_key)
    return product


def create_message_sets(
    product: CpmProduct,
    party_key: str,
    message_set_data: list[QuestionnaireResponse],
) -> DeviceReferenceData:
    message_sets = product.create_device_reference_data(
        name=EprNameTemplate.MESSAGE_SETS.format(party_key=party_key),
        environment=Environment.PROD,
    )
    for _message_set in message_set_data:
        message_sets.add_questionnaire_response(_message_set)
    return message_sets


def create_mhs_device(
    product: CpmProduct,
    party_key: str,
    mhs_device_data: QuestionnaireResponse,
    cpa_ids: list[str],
    message_sets_id: str,
) -> Device:
    mhs_device = product.create_device(
        name=EprNameTemplate.MHS_DEVICE.format(party_key=party_key),
        environment=Environment.PROD,
    )
    mhs_device.add_questionnaire_response(mhs_device_data)
    for cpa_id in cpa_ids:
        mhs_device.add_key(key_type=DeviceKeyType.CPA_ID, key_value=cpa_id)
    mhs_device.add_device_reference_data_id(
        device_reference_data_id=message_sets_id,
        path_to_data=[SdsDeviceReferenceDataPath.ALL],
    )
    return mhs_device


def create_additional_interactions(
    product: CpmProduct,
    party_key: str,
    additional_interactions_data: list[QuestionnaireResponse],
) -> DeviceReferenceData:
    additional_interactions = product.create_device_reference_data(
        name=EprNameTemplate.ADDITIONAL_INTERACTIONS.format(party_key=party_key),
        environment=Environment.PROD,
    )
    for additional_interaction in additional_interactions_data:
        additional_interactions.add_questionnaire_response(additional_interaction)
    return additional_interactions


def create_as_device(
    product: CpmProduct,
    party_key: str,
    asid: str,
    as_device_data: QuestionnaireResponse,
    message_sets_id: str,
    additional_interactions_id: str,
    as_tags: list[dict],
) -> Device:
    as_device = product.create_device(
        name=EprNameTemplate.AS_DEVICE.format(party_key=party_key, asid=asid),
        environment=Environment.PROD,
    )
    as_device.add_key(key_type=DeviceKeyType.ACCREDITED_SYSTEM_ID, key_value=asid)
    as_device.add_questionnaire_response(as_device_data)
    as_device.add_tags(tags=as_tags)
    as_device.add_device_reference_data_id(
        device_reference_data_id=message_sets_id,
        path_to_data=[SdsDeviceReferenceDataPath.ALL_INTERACTION_IDS],
    )
    as_device.add_device_reference_data_id(
        device_reference_data_id=additional_interactions_id,
        path_to_data=[SdsDeviceReferenceDataPath.ALL_INTERACTION_IDS],
    )
    return as_device
