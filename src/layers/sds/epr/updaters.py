from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.questionnaire.v1 import Questionnaire, QuestionnaireResponse
from sds.epr.constants import SdsFieldName
from sds.epr.getters import get_additional_interactions_data
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
    message_sets: DeviceReferenceData, message_set_data: list[QuestionnaireResponse]
) -> DeviceReferenceData:
    """
    Updates the MessageSets questionnaire responses with the provided message_set_data,
    with any replacements based on matching by interaction id.
    """
    interaction_id_to_qid = {
        msg_set.data[SdsFieldName.INTERACTION_ID]: msg_set.id
        for msg_sets in message_sets.questionnaire_responses.values()
        for msg_set in msg_sets
    }

    for _message_set in message_set_data:
        new_interaction_id = _message_set.data[SdsFieldName.INTERACTION_ID]
        qid_to_remove = interaction_id_to_qid.get(new_interaction_id)
        if qid_to_remove:
            message_sets.remove_questionnaire_response(
                questionnaire_id=_message_set.questionnaire_id,
                questionnaire_response_id=qid_to_remove,
            )
        message_sets.add_questionnaire_response(_message_set)
    return message_sets


def update_new_additional_interactions(
    incoming_accredited_system_interactions: set[str],
    additional_interactions: DeviceReferenceData,
    message_sets: DeviceReferenceData,
    additional_interactions_questionnaire: Questionnaire,
) -> DeviceReferenceData:
    """
    Updates the AdditionalInteractions DRD with new interactions that don't already exist
    and are not already in MessageSets DRD
    """
    mhs_interaction_ids = get_interaction_ids(message_sets)
    accredited_system_interaction_ids = get_interaction_ids(additional_interactions)

    existing_interactions = mhs_interaction_ids.union(accredited_system_interaction_ids)
    new_additional_interactions = (
        set(incoming_accredited_system_interactions) - existing_interactions
    )

    additional_interactions_data = get_additional_interactions_data(
        [{"nhs_as_svc_ia": new_additional_interactions}],
        additional_interactions_questionnaire=additional_interactions_questionnaire,
    )
    for interaction in additional_interactions_data:
        additional_interactions.add_questionnaire_response(interaction)

    return additional_interactions
