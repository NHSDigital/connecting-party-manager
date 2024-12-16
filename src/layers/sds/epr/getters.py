from domain.api.sds.query import SearchSDSDeviceQueryParams
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from sds.epr.constants import SdsFieldName
from sds.epr.tags import is_list_like, sds_metadata_to_device_tags


def _questionnaire_response_from_field_mapping_subset(
    obj: dict, questionnaire: Questionnaire, field_mapping: dict
) -> QuestionnaireResponse:
    """
    Runs Questionnaire.validate against the subset of fields in 'obj'
    that exist in 'field_mapping'
    """
    raw_translated_subset = {
        field_mapping[k]: (
            sorted(v) if is_list_like(v) else v
        )  # POSSIBLE ENHANCEMENT: can do sorting on ingestion
        for k, v in obj.items()
        if k in field_mapping and v is not None
    }
    return questionnaire.validate(raw_translated_subset)


def get_mhs_device_data(
    mhs: dict,
    mhs_device_questionnaire: Questionnaire,
    mhs_device_field_mapping: dict,
) -> QuestionnaireResponse:
    return _questionnaire_response_from_field_mapping_subset(
        obj=mhs,
        questionnaire=mhs_device_questionnaire,
        field_mapping=mhs_device_field_mapping,
    )


def get_message_set_data(
    message_handling_systems: list[dict],
    message_set_questionnaire: Questionnaire,
    message_set_field_mapping: dict,
) -> list[QuestionnaireResponse]:
    return [
        _questionnaire_response_from_field_mapping_subset(
            obj=mhs,
            questionnaire=message_set_questionnaire,
            field_mapping=message_set_field_mapping,
        )
        for mhs in message_handling_systems
    ]


def get_mhs_tags(message_handling_systems: list[dict]) -> list[dict]:
    return []


def get_additional_interactions_data(
    accredited_systems: list[dict],
    additional_interactions_questionnaire: Questionnaire,
):
    unique_interactions_ids = sorted(
        set(
            interaction_id
            for accredited_system in accredited_systems
            for interaction_id in accredited_system["nhs_as_svc_ia"]
        )
    )
    return [
        additional_interactions_questionnaire.validate(
            {str(SdsFieldName.INTERACTION_ID): interaction_id}
        )
        for interaction_id in unique_interactions_ids
    ]


def get_accredited_system_device_data(
    accredited_system: dict,
    accredited_system_questionnaire: Questionnaire,
    accredited_system_field_mapping: dict,
):
    return _questionnaire_response_from_field_mapping_subset(
        obj=accredited_system,
        questionnaire=accredited_system_questionnaire,
        field_mapping=accredited_system_field_mapping,
    )


def get_accredited_system_tags(accredited_system: dict) -> list[dict]:
    tags = sds_metadata_to_device_tags(
        data=accredited_system, model=SearchSDSDeviceQueryParams
    )
    return [dict(tag) for tag in set(tags)]
