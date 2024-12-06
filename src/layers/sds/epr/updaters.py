from domain.core.cpm_product.v1 import CpmProduct
from domain.core.device.v1 import Device
from domain.core.device_key.v1 import DeviceKey, DeviceKeyType
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.product_team.v1 import ProductTeam
from domain.core.questionnaire.v1 import QuestionnaireResponse
from domain.repository.device_repository.v1 import DeviceRepository
from sds.epr.constants import SdsFieldName
from sds.epr.creators import create_mhs_device
from sds.epr.utils import get_interaction_ids, is_mhs_device


def remove_erroneous_additional_interactions(
    message_sets: DeviceReferenceData, additional_interactions: DeviceReferenceData
) -> DeviceReferenceData:
    mhs_interaction_ids = get_interaction_ids(message_sets)
    ((questionnaire_id, questionnaire_responses),) = (
        additional_interactions.questionnaire_responses.items()
    )
    for qr in questionnaire_responses:
        additional_interaction = qr.data[SdsFieldName.INTERACTION_ID]
        if additional_interaction in mhs_interaction_ids:
            additional_interactions.remove_questionnaire_response(
                questionnaire_id=questionnaire_id, questionnaire_response_id=qr.id
            )
    return additional_interactions


def update_message_sets(
    message_sets: DeviceReferenceData, message_set_data: QuestionnaireResponse
) -> DeviceReferenceData:
    (questionnaire_id,) = message_sets.questionnaire_responses.keys()
    message_sets.remove_questionnaire(questionnaire_id)
    for _message_set in message_set_data:
        message_sets.add_questionnaire_response(_message_set)
    return message_sets


def create_or_update_mhs_device(
    device_repository: DeviceRepository,
    cpa_id: str,
    party_key: str,
    product_team: ProductTeam,
    product: CpmProduct,
    message_sets: DeviceReferenceData,
    mhs_device_data: QuestionnaireResponse,
) -> Device:
    devices = device_repository.search(
        product_team_id=product_team.id, product_id=product.id
    )
    try:
        (mhs_device,) = filter(is_mhs_device, devices)
    except ValueError:
        mhs_device = create_mhs_device(
            product=product,
            party_key=party_key,
            mhs_device_data=mhs_device_data,
            cpa_ids=[cpa_id],
        )
    else:
        cpa_id_key = DeviceKey(key_type=DeviceKeyType.CPA_ID, key_value=cpa_id)
        if cpa_id_key not in mhs_device.keys:
            mhs_device.add_key(cpa_id_key)

        if message_sets.id not in mhs_device.device_reference_data:
            mhs_device.add_device_reference_data_id(message_sets.id)

    return mhs_device
