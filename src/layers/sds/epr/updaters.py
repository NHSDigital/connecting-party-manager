from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.questionnaire.v1 import QuestionnaireResponse
from sds.epr.constants import SdsFieldName
from sds.epr.utils import get_interaction_ids


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
    if message_sets.questionnaire_responses:
        (questionnaire_id,) = message_sets.questionnaire_responses.keys()
        message_sets.remove_questionnaire(questionnaire_id)

    for _message_set in message_set_data:
        message_sets.add_questionnaire_response(_message_set)
    return message_sets
