from datetime import date, datetime, time
from functools import partial
from types import FunctionType
from typing import Generic, TypeVar

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
    human_readable_name: str
    answer_types: set[T]
    mandatory: bool
    multiple: bool
    validation_rules: set[FunctionType]
    choices: set[T]

    @validator("answer_types")
    def validate_question_type(cls, answer_types):
        invalid_types = {
            item for item in answer_types if item not in ALLOWED_QUESTION_TYPES
        }
        if invalid_types:
            raise ValueError(f"Answer types {invalid_types} are not allowed.")
        return answer_types


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
        human_readable_name: str = "",
        answer_types: set[T] = None,
        mandatory: bool = False,
        multiple: bool = False,
        validation_rules: set[FunctionType] = None,
        choices: set[T] = None,
    ):
        """
        Adds a new question to the questionnaire.
        """
        validation_rules = validation_rules or set()
        choices = choices or set()
        answer_types = answer_types or {str}

        if name in self.questions:
            raise DuplicateError(f"Question '{name}' already exists.")
        # Validate each choice is one of the allowed answer types
        if choices is not None and not all(
            any(isinstance(choice, answer_type) for answer_type in answer_types)
            for choice in choices
        ):
            raise ValueError(
                f"Choices must be of the same type as the answer types: {answer_types}."
            )
        question = Question(
            name=name,
            human_readable_name=human_readable_name,
            answer_types=answer_types,
            mandatory=mandatory,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )
        self.questions[name] = question
        return question

    @property
    def mandatory_questions(self) -> list[Question]:
        return [q for q in self.questions.values() if q.mandatory]


class QuestionnaireResponse(BaseModel):
    """
    Validates questionnaire responses against questionnaire questions
    """

    questionnaire: Questionnaire
    responses: list[tuple[str, list]]

    @validator("responses")
    def validate_mandatory_questions_are_answered(
        responses: list[tuple[str, list]], values: dict[str, Questionnaire]
    ):
        questionnaire = values.get("questionnaire")
        validate_mandatory_questions_answered(
            questionnaire_name=questionnaire.name,
            mandatory_questions=(
                [] if questionnaire is None else questionnaire.mandatory_questions
            ),
            answered_question_names=(question_name for question_name, _ in responses),
        )
        return responses

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


def validate_mandatory_questions_answered(
    questionnaire_name: str,
    mandatory_questions: list[Question],
    answered_question_names: list[tuple[str, list]],
):
    for question in mandatory_questions:
        if question.name not in answered_question_names:
            raise InvalidResponseError(
                f"Mandatory question '{question.name}' in questionnaire '{questionnaire_name}' has not been answered."
            )
    return mandatory_questions


def validate_answer_types(answer, answer_types, question_name):
    if not any(isinstance(answer, _type) for _type in answer_types):
        raise ValueError(
            f"Question '{question_name}' expects type {answer_types}. Response '{answer}' is of type '{type(answer)}'"
        )


def validate_choices(answer, choices, question_name):
    if choices and answer not in choices:
        raise ValueError(
            f"Question '{question_name}' expects choices {choices}. Response given: {answer}"
        )


def named_partial(fn, *args, **kwargs):
    _fn = partial(fn, *args, **kwargs)
    _fn.__name__ = fn.__name__
    return _fn


def validate_response_against_question(answers: list, question: Question):
    if not question.multiple and len(answers) > 1:
        raise InvalidResponseError(
            f"Question '{question.name}' does not allow multiple responses. Response given: {answers}."
        )
    errors = []
    answer_types_rule = named_partial(
        validate_answer_types,
        answer_types=question.answer_types,
        question_name=question.name,
    )
    choices_rule = named_partial(
        validate_choices, choices=question.choices, question_name=question.name
    )

    for answer in answers:
        for validation_rule in question.validation_rules.union(
            [answer_types_rule, choices_rule]
        ):
            try:
                validation_rule(answer)
            except ValueError as e:
                errors.append(
                    f"Question '{question.name}' rule '{validation_rule.__name__}' failed validation for response '{answer}' with error: {e}."
                )
    if errors:
        raise InvalidResponseError("\n".join(errors))
    return answers
