from types import FunctionType

from domain.core.error import ConfigurationError
from domain.core.questionnaire.v1 import Questionnaire, QuestionnaireResponse


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
    generation_strategy: FunctionType,
    **generation_strategy_kwargs,
) -> QuestionnaireResponse:
    check_expected_questionnaire_response_fields(
        questionnaire=questionnaire, response=questionnaire_response
    )
    generation_strategy(response=questionnaire_response, **generation_strategy_kwargs)
    return questionnaire.validate(data=questionnaire_response)
