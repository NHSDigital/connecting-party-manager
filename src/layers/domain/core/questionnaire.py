from datetime import date, datetime, time
from types import FunctionType
from typing import Generic, Type, TypeVar

from domain.core.error import DuplicateError, InvalidResponseError
from domain.core.validation import ENTITY_NAME_REGEX
from pydantic import BaseModel, Field, validator

# from domain.core.questionnaire_validation_custom_rules import url

T = TypeVar("T")
A = {str, int, bool, datetime, float, date, time}  # allowed question types


class Question(BaseModel, Generic[T]):
    """
    A single Questionnaire Question
    """

    class Config:
        """
        Validation rules are not pydantic classes
        """

        arbitrary_types_allowed = True

    name: str
    type: T
    multiple: bool
    validation_rules: set[FunctionType] = None
    choices: set[T] = None

    @validator("type")
    def validate_question_type(cls, type):
        if type not in A:
            raise ValueError
        return type


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
        type: Type = str,
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
            isinstance(choice, type) for choice in choices
        ):
            raise ValueError(
                f"Choices must be of the same type as the question type: {type}"
            )

        question = Question[type](
            name=name,
            type=type,
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

    @validator("responses", each_item=True)
    def validate_responses(
        response: tuple[str, list], values: dict[str, Questionnaire]
    ):
        questionnaire = values.get("questionnaire")
        question_name = response[0]
        if questionnaire is not None:
            questionnaire_name = questionnaire.name
            question = questionnaire.questions.get(question_name)
            if question is None:
                raise InvalidResponseError(
                    f"Unexpected answer for the question '{question_name}'. The questionnaire '{questionnaire_name}' does not contain this question."
                )
            validate_response_against_question(response=response, question=question)
        return response


def validate_response_against_question(response: tuple[str, list], question: Question):
    answers = response[1]

    if not question.multiple and len(answers) > 1:
        raise InvalidResponseError(
            f"Question '{question.name}' does not allow multiple responses. Response given: {answers}."
        )

    errors = (
        []
    )  # accumulate errors here for multianswer question and raise under a single ValueError
    for answer in answers:
        if not isinstance(answer, question.type):
            errors.append(
                f"Question '{question.name}' expects type {question.type}. Response given: {answer}."
            )

        if question.validation_rules is not None:
            for validation_rule in question.validation_rules:
                try:
                    validation_rule(answer)
                except ValueError as e:
                    errors.append(
                        f"Question '{question.name}' validation failed for response: {answer}. Error: {str(e)}"
                    )

        if question.choices and answer not in question.choices:
            errors.append(
                f"Question '{question.name}' expects choices {question.choices}. Response given: {answer}."
            )

    if errors:
        raise InvalidResponseError("\n".join(errors))

    return response
