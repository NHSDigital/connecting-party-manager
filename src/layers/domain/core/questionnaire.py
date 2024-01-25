from datetime import date, datetime, time
from enum import Enum

from domain.core.error import DuplicateError, InvalidResponseError
from domain.core.validation import ENTITY_NAME_REGEX
from pydantic import BaseModel, Field

# import validators


class QuestionType(Enum):
    """
    The data type of the question
    """

    STRING = str
    INT = int
    BOOL = bool
    DATE_TIME = datetime
    DECIMAL = float
    DATE = date
    TIME = time


class Question(BaseModel):
    """
    A single Questionnaire Question
    """

    name: str
    type: QuestionType
    multiple: bool
    validation_rules: list[str] = []
    choices: list[str] = []


class Questionnaire(BaseModel):
    """
    A Questionnaire represents a collection of Questions, in a specific order.
    """

    name: str = Field(regex=ENTITY_NAME_REGEX)
    version: int
    questions: list[Question] = []

    def __contains__(self, question_name: str) -> bool:
        """
        Returns true if the question specified exists within the questionnaire
        """

        return question_name in (q.name for q in self.questions)

    def add_question(
        self,
        name: str,
        type: QuestionType = QuestionType.STRING,
        multiple: bool = False,
        validation_rules: list[str] = [],
        choices: list[str] = [],
    ):
        """
        Adds a new question to the questionnaire.
        """
        for question in self.questions:
            if name == question.name:
                raise DuplicateError(f"Question exists: {name}")

        question = Question(
            name=name,
            type=type,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )
        self.questions.append(question)
        return question


class QuestionnaireResponse(BaseModel):
    """
    Validates questionnaire responses against questionnaire questions
    """

    responses: dict
    questionnaire: Questionnaire

    def validate_question_response_type(self, question_name, response):
        question = next(
            (q for q in self.questionnaire.questions if q.name == question_name), {}
        )
        question_type = question.type
        if isinstance(response, list):
            for item in response:
                if not isinstance(item, question.type.value):
                    return False, question_type
        else:
            if not isinstance(response, question.type.value):
                return False, question_type

        return True, None

    def validate_questionnaire_responses_types(self):
        invalid_responses_types = []
        for question_name, response in self.responses.items():
            is_valid, failed_type = self.validate_question_response_type(
                question_name, response
            )

            if not is_valid:
                invalid_responses_types.append((question_name, response, failed_type))

        return invalid_responses_types

    def validate_question_response_rules(self, question_name, response):
        question = next(
            (q for q in self.questionnaire.questions if q.name == question_name), {}
        )

        validation_rules = question.validation_rules

        failed_rules = []

        if isinstance(response, list):
            for item in response:
                for validation_rule in validation_rules:
                    if validation_rule == "text":
                        if not (isinstance(item, str) and len(item) > 0):
                            failed_rules.append(validation_rule)

                    if validation_rule == "number2":
                        if not item == 2:
                            failed_rules.append(validation_rule)

                    # if validation_rule == "url":
                    #     if not validators.url(item):
                    #         failed_rules.append(validation_rule)
        else:
            for validation_rule in validation_rules:
                if validation_rule == "text":
                    if not (isinstance(response, str) and len(response) > 0):
                        failed_rules.append(validation_rule)

                if validation_rule == "number2":
                    if not response == 2:
                        failed_rules.append(validation_rule)

                # if validation_rule == "url":
                #     if not validators.url(response):
                #         failed_rules.append(validation_rule)

                # Add more validation criteria for different question types as needed

        if len(failed_rules) == 0:
            return True, None  # All validation rules passed
        else:
            return False, failed_rules

    def validate_questionnaire_responses_rules(self):
        invalid_responses_rules = []
        for question_name, response in self.responses.items():
            is_valid, failed_rules = self.validate_question_response_rules(
                question_name, response
            )

            if not is_valid:
                invalid_responses_rules.append((question_name, response, failed_rules))

        return invalid_responses_rules

    def validate_question_response_choices(self, question_name, response):
        question = next(
            (q for q in self.questionnaire.questions if q.name == question_name), {}
        )
        valid_choices = question.choices
        if isinstance(response, list):
            for item in response:
                # Check if the question has choices and if each response is one of the valid choices
                if valid_choices and item not in valid_choices:
                    return False, valid_choices

        elif valid_choices and response not in valid_choices:
            return False, valid_choices
        return True, None

    def validate_questionnaire_responses_choices(self):
        invalid_responses_choices = []
        for question_name, response in self.responses.items():
            is_valid, valid_choices = self.validate_question_response_choices(
                question_name, response
            )

            if not is_valid:
                invalid_responses_choices.append(
                    (question_name, response, valid_choices)
                )

        return invalid_responses_choices

    def validate_responses_correspond_to_questionnaire(self):
        # Check if questionnaire responses correspond to the questions in the questionnaire
        for question_name in self.responses:
            if question_name not in [q.name for q in self.questionnaire.questions]:
                raise InvalidResponseError(
                    f"Unexpected answer for the question '{question_name}'. The questionnaire '{self.questionnaire.name}' does not contain this question."
                )
        return True

    def validate_multiple_responses_allowed(self):
        invalid_responses = []
        # check if multiple responses gievn when not expected
        for q in self.questionnaire.questions:
            if q.multiple == False and isinstance(
                self.responses[q.name], list
            ):  # lenght of list >1? Single response as a list?
                invalid_responses.append((q.name, self.responses[q.name]))

        if len(invalid_responses) > 0:
            invalid_responses_given = []
            for q.name, self.responses[q.name] in invalid_responses:
                invalid_response = f"Question '{q.name}' does not allow multiple responses. Response given: {self.responses[q.name]}."
                invalid_responses_given.append(invalid_response)

            raise InvalidResponseError(invalid_responses_given)

        return True

    def validate_and_get_invalid_responses(self):
        self.validate_responses_correspond_to_questionnaire()
        self.validate_multiple_responses_allowed()

        invalid_responses_types = self.validate_questionnaire_responses_types()
        invalid_responses_rules = self.validate_questionnaire_responses_rules()
        invalid_responses_choices = self.validate_questionnaire_responses_choices()

        if (
            not invalid_responses_types
            and not invalid_responses_rules
            and not invalid_responses_choices
        ):
            return [
                f"invalid response types: {invalid_responses_types}",
                f"invalid response rules: {invalid_responses_rules}",
                f"invalid response choices: {invalid_responses_choices}",
            ]

        else:
            failed_validation_types_explained = []
            failed_validation_rules_explained = []
            failed_validation_choices_explained = []
            for question_name, response, failed_type in invalid_responses_types:
                failed_validation_type = f"Question '{question_name}': {response}. Expected type: {failed_type}."
                failed_validation_types_explained.append(failed_validation_type)

            for question_name, response, validation_rules in invalid_responses_rules:
                failed_validation = f"Question '{question_name}': {response} failed validation for rule(s): {validation_rules}."
                failed_validation_rules_explained.append(failed_validation)

            for question_name, response, valid_choices in invalid_responses_choices:
                failed_validation = f"Question '{question_name}': {response} failed validation as not in choices: {valid_choices}."
                failed_validation_choices_explained.append(failed_validation)

            raise InvalidResponseError(
                f"Invalid response types: {failed_validation_types_explained}. Invalid validation rules: {failed_validation_rules_explained}. Invalid response choices: {failed_validation_choices_explained}"
            )
