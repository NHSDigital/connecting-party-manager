from datetime import datetime
from typing import Optional

from attr import dataclass
from domain.core.enum import Status
from domain.core.error import InvalidResponseError
from domain.core.event import Event
from domain.core.timestamp import now
from pydantic import BaseModel, Field, validator

from .v1 import Questionnaire as QuestionnaireV1
from .v1 import (
    validate_mandatory_questions_answered,
    validate_response_against_question,
)


@dataclass(kw_only=True, slots=True)
class QuestionnaireResponseUpdatedEvent(Event):
    entity_id: str
    entity_keys: list
    entity_tags: list
    questionnaire_responses: list["QuestionnaireResponse"]
    updated_on: Optional[str] = None


class Questionnaire(QuestionnaireV1):
    def respond(self, responses: list[dict[str, list]]):
        return QuestionnaireResponse(
            questionnaire=self, questionnaire_id=self.id, answers=responses
        )


class QuestionnaireResponse(BaseModel):
    """
    Validates questionnaire responses against questionnaire questions
    Answers are of the form:
        [{"question_name": ["answer_1", ..., "answer_n"]}]

    where n > 1 if Question.multiple is true for the Question in Questionnaire
    with the matching Question.name
    """

    questionnaire: Optional[Questionnaire] = Field(exclude=True, default=None)
    questionnaire_id: str
    answers: list[dict[str, list]]
    created_on: datetime = Field(default_factory=now)
    status: Status = Field(default=Status.ACTIVE)

    @validator("answers")
    def validate_mandatory_questions_are_answered(
        cls, answers: list[dict[str, list]], values: dict[str, Questionnaire]
    ):
        questionnaire = values.get("questionnaire")
        if questionnaire is None:
            return answers
        validate_mandatory_questions_answered(
            questionnaire_name=questionnaire.name,
            mandatory_questions=(
                [] if questionnaire is None else questionnaire.mandatory_questions
            ),
            answered_question_names=[
                question_name for (question_name, _), in map(dict.items, answers)
            ],
        )
        return answers

    @validator("answers", each_item=True)
    def validate_responses(
        cls, answer: dict[str, list], values: dict[str, Questionnaire]
    ):
        questionnaire = values.get("questionnaire")
        if questionnaire is None:
            return answer
        ((question_name, answers),) = answer.items()
        if questionnaire is not None:
            questionnaire_name = questionnaire.name
            question = questionnaire.questions.get(question_name)
            if question is None:
                raise InvalidResponseError(
                    f"Unexpected answer for the question '{question_name}'. The questionnaire '{questionnaire_name}' does not contain this question."
                )
            validate_response_against_question(question=question, answers=answers)
        return answer

    def get_response(self, question_name) -> list:
        for response in self.answers:
            value = response.get(question_name)
            if value is not None:
                return value
        return []

    @property
    def flat_answers(self) -> dict[str, any]:
        return {
            question: (answer[0] if len(answer) == 1 else answer)
            for question_answer in self.answers
            for question, answer in question_answer.items()
        }
