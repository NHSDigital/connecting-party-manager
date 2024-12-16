from domain.core.error import ConfigurationError
from domain.core.questionnaire.v1 import Questionnaire, QuestionnaireResponse
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)


def check_expected_questionnaire_response_fields(
    questionnaire: Questionnaire, response: dict
):
    expected_fields = set(questionnaire.user_provided_fields)
    payload_fields = set(response.keys())

    unexpected_fields = payload_fields - expected_fields
    if unexpected_fields:
        raise ConfigurationError(
            f"Payload contains unexpected fields: {unexpected_fields}. "
            f"Expected fields are: {sorted(expected_fields)}."
        )


def process_and_validate_questionnaire_response(
    questionnaire: Questionnaire,
    questionnaire_response: dict,
    party_key: str,
    instance: QuestionnaireInstance,
) -> QuestionnaireResponse:
    check_expected_questionnaire_response_fields(questionnaire, questionnaire_response)
    questionnaire.generate_system_fields(
        questionnaire_response, instance=instance, party_key=party_key
    )
    return questionnaire.validate(data=questionnaire_response)
