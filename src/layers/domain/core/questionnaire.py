from datetime import date, datetime, time
from types import FunctionType
from typing import Generic, Type, TypeVar

from pydantic import BaseModel, Field, validator

from .error import DuplicateError, InvalidResponseError
from .validation import ENTITY_NAME_REGEX

T = TypeVar("T")
ALLOWED_QUESTION_TYPES = {str, int, bool, datetime, float, date, time}


class Question(BaseModel, Generic[T]):
    """
    A single Questionnaire Question
    """

    class Config:
        """
        Validation rules are not pydantic classes
        """

        arbitrary_types_allowed = True

    name: str = Field(regex=ENTITY_NAME_REGEX)
    answer_type: T
    mandatory: bool
    multiple: bool
    validation_rules: set[FunctionType] = None
    choices: set[T] = None

    @validator("answer_type")
    def validate_question_type(cls, answer_type):
        if answer_type not in ALLOWED_QUESTION_TYPES:
            raise ValueError(f"Answer type {answer_type} is not allowed.")
        return answer_type


class Questionnaire(BaseModel):
    """
    A Questionnaire represents a collection of Questions, in a specific order.
    """

    name: str = Field(regex=ENTITY_NAME_REGEX)
    version: int
    questions: dict[str, Question] = Field(default_factory=dict)

    def __contains__(self, question_name: str) -> bool:
        """
        Returns true if the question specified exists within the questionnaire
        """

        return question_name in self.questions

    def add_question(
        self,
        name: str,
        answer_type: Type = str,
        mandatory: bool = False,
        multiple: bool = False,
        validation_rules: set[FunctionType] = None,
        choices: set[T] = None,
    ):
        """
        Adds a new question to the questionnaire.
        """
        if name in self.questions:
            raise DuplicateError(f"Question '{name}' already exists.")

        # Validate choices are of the same type as the question type
        if choices is not None and not all(
            isinstance(choice, answer_type) for choice in choices
        ):
            raise ValueError(
                f"Choices must be of the same type as the question type: {answer_type}."
            )

        question = Question(
            name=name,
            answer_type=answer_type,
            mandatory=mandatory,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )

        self.questions[name] = question
        return question


class QuestionnaireResponse(BaseModel):
    """
    Validates questionnaire responses against questionnaire questions
    """

    questionnaire: Questionnaire
    responses: list[tuple[str, list]]

    # validate_mandatory_questions_answered(questionnaire, responses)

    @validator("responses", each_item=True)
    def validate_responses(
        response: tuple[str, list], values: dict[str, Questionnaire]
    ):
        questionnaire = values.get("questionnaire")
        question_name, answers = response
        if questionnaire is not None:
            questionnaire_name = questionnaire.name
            question = questionnaire.questions.get(question_name)
            if question is None:
                raise InvalidResponseError(
                    f"Unexpected answer for the question '{question_name}'. The questionnaire '{questionnaire_name}' does not contain this question."
                )
            validate_response_against_question(question=question, answers=answers)
        return response


def validate_response_against_question(answers: list, question: Question):
    if not question.multiple and len(answers) > 1:
        raise InvalidResponseError(
            f"Question '{question.name}' does not allow multiple responses. Response given: {answers}."
        )

    errors = (
        []
    )  # accumulate errors here for multianswer question and raise under a single ValueError
    for answer in answers:
        if not isinstance(answer, question.answer_type):
            errors.append(
                f"Question '{question.name}' expects type {question.answer_type}. Response '{answer}' is of type '{type(answer)}'."
            )

        if question.validation_rules is not None:
            for validation_rule in question.validation_rules:
                try:
                    validation_rule(answer)
                except ValueError as e:
                    errors.append(
                        f"Question '{question.name}' rule '{validation_rule.__name__}' failed validation for response '{answer}' with error: {e}."
                    )

        if question.choices and answer not in question.choices:
            errors.append(
                f"Question '{question.name}' expects choices {question.choices}. Response given: {answer}."
            )

    if errors:
        raise InvalidResponseError("\n".join(errors))

    return answers


# Logic for validating mandatory questions - needs to be implemented
def validate_mandatory_questions_answered(
    questionnaire: Questionnaire, responses: list[tuple[str, list]]
):
    if questionnaire is not None:
        questionnaire_name = questionnaire.name
        # If question is not present in the response, check if it is mandatory
        for question in questionnaire.questions.values():
            if question.mandatory and (question.name not in dict(responses)):
                raise InvalidResponseError(
                    f"Mandatory question '{question.name}' in questionnaire '{questionnaire_name}' has not been answered."
                )
