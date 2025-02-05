from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.questionnaire.v1 import Questionnaire, QuestionnaireResponse
from sds.epr.constants import SdsFieldName
from sds.epr.getters import get_additional_interactions_data
from sds.epr.utils import get_interaction_ids


class UnexpectedModification(Exception): ...


JSON_SCHEMA_PROPERTIES_KEYWORD = "properties"
JSON_SCHEMA_REQUIRED_KEYWORD = "required"
JSON_SCHEMA_TYPE_KEYWORD = "type"
JSON_SCHEMA_ARRAY_FIELD_TYPE = "array"


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
) -> tuple[DeviceReferenceData, set[str]]:
    """
    Updates the AdditionalInteractions DRD with new interactions that don't already exist
    and are not already in MessageSets DRD
    Returns the new interactions added, to be used to add tags to existing AS devices
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

    return additional_interactions, new_additional_interactions


def ldif_add_to_field_in_questionnaire(
    field_name: str,
    new_values: list[str],
    current_data: dict[str, list[str] | str],
    questionnaire: Questionnaire,
) -> QuestionnaireResponse:
    _schema = questionnaire.json_schema[JSON_SCHEMA_PROPERTIES_KEYWORD][field_name]
    expected_type = _schema[JSON_SCHEMA_TYPE_KEYWORD]
    expect_list_type = expected_type == JSON_SCHEMA_ARRAY_FIELD_TYPE
    current_value = current_data.get(field_name, [])

    # Elaborate the possible logic routes
    extend_values_on_list_type = expect_list_type and current_value
    set_values_on_list_type = expect_list_type and not current_value
    set_only_value_on_non_list_type = (
        not expect_list_type and not current_value and len(new_values) == 1
    )

    # Route the operation
    updated_value = None
    if extend_values_on_list_type:
        updated_value = current_value + list(new_values)
    elif set_values_on_list_type:
        updated_value = list(new_values)
    elif set_only_value_on_non_list_type:
        (_new_value,) = new_values
        updated_value = _new_value
    else:
        # Should not be reachable, but better to bail to avoid unexpected side-effects
        raise UnexpectedModification(
            f"No strategy implemented for field name '{field_name}' "
            f"of expected type {expected_type} with "
            f"values {new_values}, given current value '{current_value}'"
        )

    # Copy, update and validate the new data
    updated_data = dict(current_data)
    updated_data[field_name] = updated_value
    return questionnaire.validate(updated_data)


def ldif_modify_field_in_questionnaire(
    field_name: str,
    new_values: list[str],
    current_data: dict[str, list[str] | str],
    questionnaire: Questionnaire,
) -> QuestionnaireResponse:
    _schema = questionnaire.json_schema[JSON_SCHEMA_PROPERTIES_KEYWORD][field_name]
    expected_type = _schema[JSON_SCHEMA_TYPE_KEYWORD]
    expect_list_type = expected_type == JSON_SCHEMA_ARRAY_FIELD_TYPE

    # Elaborate the possible logic routes
    replace_list_type = expect_list_type
    set_only_value_on_non_list_type = not expect_list_type and len(new_values) == 1

    # Route the operation
    updated_value = None
    if replace_list_type:
        updated_value = list(new_values)
    elif set_only_value_on_non_list_type:
        (_new_value,) = new_values
        updated_value = _new_value
    else:
        # Should not be reachable, but better to bail to avoid unexpected side-effects
        raise UnexpectedModification(
            f"No strategy implemented for field name '{field_name}' "
            f"of expected type {expected_type} with "
            f"values {new_values}.'"
        )

    # Copy, update and validate the new data
    updated_data = dict(current_data)
    updated_data[field_name] = updated_value
    return questionnaire.validate(updated_data)


def ldif_remove_field_from_questionnaire(
    field_name: str,
    new_values: list[str],  # noqa
    current_data: dict[str, list[str] | str],
    questionnaire: Questionnaire,
) -> QuestionnaireResponse:
    required_fields = set(
        questionnaire.json_schema.get(JSON_SCHEMA_REQUIRED_KEYWORD, ())
    )
    if field_name in required_fields:
        raise UnexpectedModification(f"Cannot remove required field '{field_name}'")

    # Copy, update and validate the new data
    updated_data = dict(current_data)
    updated_data.pop(field_name)
    return questionnaire.validate(updated_data)
