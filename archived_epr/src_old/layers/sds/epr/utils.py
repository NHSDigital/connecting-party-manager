from domain.core.device.v1 import Device
from domain.core.device_reference_data.v1 import DeviceReferenceData
from domain.core.questionnaire.v1 import QuestionnaireResponse
from sds.epr.constants import (
    ADDITIONAL_INTERACTIONS_SUFFIX,
    AS_DEVICE_SUFFIX,
    MESSAGE_SETS_SUFFIX,
    MHS_DEVICE_SUFFIX,
    SdsFieldName,
)


def is_message_set_device_reference_data(
    device_reference_data: DeviceReferenceData,
) -> bool:
    return device_reference_data.name.endswith(MESSAGE_SETS_SUFFIX)


def is_additional_interactions_device_reference_data(
    device_reference_data: DeviceReferenceData,
) -> bool:
    return device_reference_data.name.endswith(ADDITIONAL_INTERACTIONS_SUFFIX)


def is_mhs_device(device: Device) -> bool:
    return device.name.endswith(MHS_DEVICE_SUFFIX)


def is_as_device(device: Device) -> bool:
    return device.name.endswith(AS_DEVICE_SUFFIX)


def get_interaction_ids(
    message_sets_or_additional_interactions: DeviceReferenceData,
) -> set[str]:
    questionnaire_responses = (
        message_sets_or_additional_interactions.questionnaire_responses.values()
    )

    try:
        (questionnaire_responses,) = (
            message_sets_or_additional_interactions.questionnaire_responses.values()
        )
    except ValueError:
        interaction_ids = set()
    else:
        interaction_ids = {
            qr.data[SdsFieldName.INTERACTION_ID] for qr in questionnaire_responses
        }

    return interaction_ids


def filter_message_set_by_cpa_id(
    message_sets: DeviceReferenceData, cpa_id: str
) -> QuestionnaireResponse:
    (message_sets_questionnaire_id,) = message_sets.questionnaire_responses.keys()
    (message_set,) = (
        qr
        for qr in message_sets.questionnaire_responses[message_sets_questionnaire_id]
        if qr.data[SdsFieldName.CPA_ID] == cpa_id
    )

    return message_set
