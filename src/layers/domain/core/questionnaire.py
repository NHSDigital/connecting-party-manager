from datetime import date, datetime, time
from functools import partial
from types import FunctionType
from typing import Self

import orjson
from attr import dataclass, field
from pydantic import Field, validator

from .base import BaseModel
from .error import DuplicateError, InvalidResponseError
from .event import Event
from .validation import ENTITY_NAME_REGEX


class CaseInsensitiveString(str):
    pass


class InvalidChoiceType(ValueError):
    pass


class TooManyAnswerTypes(ValueError):
    pass


ALLOWED_QUESTION_TYPES = {
    str,
    int,
    bool,
    datetime,
    float,
    date,
    time,
    CaseInsensitiveString,
}


@dataclass(kw_only=True, slots=True)
class _Question:
    name: str
    human_readable_name: str
    answer_types: list[str]
    mandatory: bool
    multiple: bool
    validation_rules: list[str]
    choices: list


@dataclass(kw_only=True, slots=True)
class QuestionnaireInstanceEvent(Event):
    """Event for when a Questionnaire has been responded to by an Entity"""

    entity_id: str
    questionnaire_id: str
    name: str
    version: int
    questions: dict[str, _Question]
    _trust: bool = field(alias="_trust", default=False)


@dataclass(kw_only=True, slots=True)
class QuestionnaireResponseAddedEvent(Event):
    entity_id: str
    questionnaire_id: str
    questionnaire_response_index: int
    responses: list[dict[str, list]]
    _trust: bool = field(alias="_trust", default=False)


@dataclass(kw_only=True, slots=True)
class QuestionnaireResponseUpdatedEvent(Event):
    entity_id: str
    questionnaire_id: str
    questionnaire_response_index: int
    responses: list[dict[str, list]]


@dataclass(kw_only=True, slots=True)
class QuestionnaireResponseDeletedEvent(Event):
    entity_id: str
    questionnaire_id: str
    questionnaire_response_index: int


class Question(BaseModel):
    """
    A single Questionnaire Question
    """

    name: str = Field(regex=ENTITY_NAME_REGEX)
    human_readable_name: str
    answer_types: set[type]
    mandatory: bool
    multiple: bool
    validation_rules: set[FunctionType]
    choices: set

    @validator("answer_types")
    def validate_question_type(cls, answer_types):
        invalid_types = {
            item for item in answer_types if item not in ALLOWED_QUESTION_TYPES
        }
        if invalid_types:
            raise ValueError(f"Answer types {invalid_types} are not allowed.")
        return answer_types

    def dict(self, **kwargs):
        _data = self.json(**kwargs)
        return orjson.loads(_data)


def choice_type_matches_answer_types(choice, answer_types: set):
    """
    Choice either exactly matches the answer type, or the
    answer type is a subclass of the choice type
    """
    return any(
        isinstance(choice, answer_type)
        or (isinstance(choice, str) and answer_type is CaseInsensitiveString)
        for answer_type in answer_types
    )


class Questionnaire(BaseModel):
    """
    A Questionnaire represents a collection of Questions, in a specific order.
    """

    name: str = Field(regex=ENTITY_NAME_REGEX)
    version: int
    questions: dict[str, Question] = Field(default_factory=dict)

    @property
    def id(self):
        return f"{self.name}/{self.version}"

    def __contains__(self, question_name: str) -> bool:
        """
        Returns true if the question specified exists within the questionnaire
        """
        return question_name in self.questions

    def __hash__(self):
        question_names = ".".join(self.questions)
        return hash(f"{self.id}.{question_names}")

    def __eq__(self, other: Self):
        return self.id == other.id

    def add_question(
        self,
        name: str,
        human_readable_name: str = "",
        answer_types: set = None,
        mandatory: bool = False,
        multiple: bool = False,
        validation_rules: set[FunctionType] = None,
        choices: set = None,
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
        if choices and not all(
            choice_type_matches_answer_types(choice=choice, answer_types=answer_types)
            for choice in choices
        ):
            raise InvalidChoiceType(
                f"Question '{name}': Choices ({choices}) must be of the same type as the answer types: {answer_types}."
            )

        if choices and len(answer_types) > 1:
            raise TooManyAnswerTypes(
                f"Question '{name}': There must only be one answer type (provided answer types: '{answer_types}') "
                f"if choices are specified (provided choices: '{choices}')"
            )

        if answer_types == {CaseInsensitiveString}:
            choices = set(map(str.lower, choices))

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

    def respond(self, responses: list[dict[str, list]]):
        return QuestionnaireResponse(questionnaire=self, responses=responses)


class QuestionnaireResponse(BaseModel):
    """
    Validates questionnaire responses against questionnaire questions
    Responses is of the form:
        ["question_name": ["answer_1", ..., "answer_n"]]

    where n > 1 if Question.multiple is true for the Question in Questionnaire
    with the matching Question.name
    """

    questionnaire: Questionnaire
    responses: list[dict[str, list]]

    @validator("responses")
    def validate_mandatory_questions_are_answered(
        responses: list[dict[str, list]], values: dict[str, Questionnaire]
    ):
        questionnaire = values.get("questionnaire")
        validate_mandatory_questions_answered(
            questionnaire_name=questionnaire.name,
            mandatory_questions=(
                [] if questionnaire is None else questionnaire.mandatory_questions
            ),
            answered_question_names=[
                question_name for (question_name, _), in map(dict.items, responses)
            ],
        )
        return responses

    @validator("responses", each_item=True)
    def validate_responses(response: dict[str, list], values: dict[str, Questionnaire]):
        questionnaire = values.get("questionnaire")
        ((question_name, answers),) = response.items()
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
    answered_question_names: list[str],
):
    for question in mandatory_questions:
        if question.name not in answered_question_names:
            raise InvalidResponseError(
                f"Mandatory question '{question.name}' in questionnaire '{questionnaire_name}' has not been answered."
            )
    return mandatory_questions


def validate_answer_types(answer, answer_types, question_name):
    if not choice_type_matches_answer_types(choice=answer, answer_types=answer_types):
        raise ValueError(
            f"Question '{question_name}' expects type {answer_types}. Response '{answer}' is of type '{type(answer)}'"
        )


def validate_choices(answer, choices, question_name, answer_types):
    if answer_types == {CaseInsensitiveString}:
        answer = answer.lower()

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
        validate_choices,
        choices=question.choices,
        question_name=question.name,
        answer_types=question.answer_types,
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
