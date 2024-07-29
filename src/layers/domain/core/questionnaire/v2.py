from datetime import datetime

from domain.core.timestamp import now
from pydantic import Field

from .v1 import Questionnaire as QuestionnaireV1
from .v1 import QuestionnaireResponse as QuestionnaireResponseV1


class Questionnaire(QuestionnaireV1):
    def respond(self, responses: list[dict[str, list]]):
        return QuestionnaireResponse(questionnaire=self, responses=responses)


class QuestionnaireResponse(QuestionnaireResponseV1):
    """
    Validates questionnaire responses against questionnaire questions
    Responses is of the form:
        [{"question_name": ["answer_1", ..., "answer_n"]}]

    where n > 1 if Question.multiple is true for the Question in Questionnaire
    with the matching Question.name
    """

    questionnaire: Questionnaire
    responses: list[dict[str, list]]
    created_on: datetime = Field(default_factory=now)
