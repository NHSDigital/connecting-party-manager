from datetime import date, datetime, time
from enum import Enum

from domain.core.error import DuplicateError, InvalidResponseError
from domain.core.validation import ENTITY_NAME_REGEX
from pydantic import BaseModel, Field, ValidationError

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
    _questions: list[Question] = []

    def __contains__(self, question_name: str) -> bool:
        """
        Returns true if the question specified exists within the questionnaire
        """

        return question_name in (q.name for q in self._questions)

    def add_question(
        self,
        name: str,
        type: QuestionType = QuestionType.STRING,
        multiple: bool = False,
        validation_rules: list[str] = [],
        choices: list[str] = [],
    ):
        """
        Adds a new question to the questionnaire.  Once a questionnaire is
        locked this method will throw an error.
        """

        if name in self:
            raise DuplicateError(f"Question exists: {name}")
        result = Question(
            name=name,
            type=type,
            multiple=multiple,
            validation_rules=validation_rules,
            choices=choices,
        )
        self._questions.append(result)
        return result


class QuestionnaireResponse(BaseModel):
    """
    Represents a Questionnaire response mapping Questions to Responses.
    """

    responses: dict


class QuestionnaireResponseValidator(BaseModel):
    """
    Validates questionnaire responses against questionnaire questions are of the correct type, meet any validation criteria and .
    """

    questionnaire: Questionnaire
    responses: dict

    def validate_question_response_type(self, question_name, response):
        question = next(
            (q for q in self.questionnaire._questions if q.name == question_name), {}
        )
        question_type = question.type
        if question.multiple:
            if not isinstance(response, list):
                response = [response]
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
            (q for q in self.questionnaire._questions if q.name == question_name), {}
        )

        validation_rules = question.validation_rules

        if question.multiple:
            if not isinstance(response, list):
                response = [response]
            for item in response:
                for validation_rule in validation_rules:
                    if validation_rule == "text":
                        if not (isinstance(item, str) and len(item) > 0):
                            return (
                                False,
                                validation_rule,
                            )
        else:
            for validation_rule in validation_rules:
                if validation_rule == "text":
                    if not (isinstance(response, str) and len(response) > 0):
                        return (
                            False,
                            validation_rule,
                        )  # Returns at first failed rule only - not showing all failed criteria
                # if validation_rule == "url":
                #     if not validators.url(response):
                #         return (False, validation_rule)
                # Add more validation criteria for different question types as needed

        return True, None  # All validation rules passed

    def validate_questionnaire_responses_rules(self):
        invalid_responses_rules = []
        for question_name, response in self.responses.items():
            is_valid, failed_rule = self.validate_question_response_rules(
                question_name, response
            )

            if not is_valid:
                invalid_responses_rules.append((question_name, response, failed_rule))

        return invalid_responses_rules

    def validate_question_response_choices(self, question_name, response):
        question = next(
            (q for q in self.questionnaire._questions if q.name == question_name), {}
        )
        valid_choices = question.choices
        if question.multiple:
            if not isinstance(response, list):
                response = [response]
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

    def validate_and_get_invalid_responses(self):
        # Use Pydantic to validate the overall structure of the responses
        try:
            questionnaire_response = QuestionnaireResponse.parse_obj(
                {"responses": self.responses}
            )
        except ValidationError as e:
            raise InvalidResponseError(f"Invalid response structure: {e.errors()}")

        # Check if questionnaire responses correspond to the questions in the questionnaire
        for question_name in self.responses:
            if question_name not in [q.name for q in self.questionnaire._questions]:
                raise InvalidResponseError(
                    f"Unexpected answer for the question '{question_name}'. The questionnaire '{self.questionnaire.name}' does not contain this question."
                )  # should this message be different? Wrong questionnaire answered?

        invalid_responses_types = self.validate_questionnaire_responses_types()
        invalid_responses_rules = self.validate_questionnaire_responses_rules()
        invalid_responses_choices = self.validate_questionnaire_responses_choices()

        if (
            not invalid_responses_types
            and not invalid_responses_rules
            and not invalid_responses_choices
        ):
            return "All responses are valid."

        else:
            failed_validation_types_explained = []
            failed_validation_rules_explained = []
            failed_validation_choices_explained = []
            for question_name, response, failed_type in invalid_responses_types:
                failed_validation_type = f"Question '{question_name}': {response} (Failed validation type: {failed_type})"
                failed_validation_types_explained.append(failed_validation_type)

            for question_name, response, validation_rule in invalid_responses_rules:
                failed_validation = f"Question '{question_name}': {response} (Failed validation for rule: {validation_rule})"
                failed_validation_rules_explained.append(failed_validation)

            for question_name, response, valid_choices in invalid_responses_choices:
                failed_validation = f"Question '{question_name}': {response} (Failed validation as not in choices: {valid_choices})"
                failed_validation_choices_explained.append(failed_validation)

            raise InvalidResponseError(
                f"Invalid response types: {failed_validation_types_explained}. Invalid validation rules: {failed_validation_rules_explained}. Invalid response choices: {failed_validation_choices_explained}"
            )


# Example Usage:

# Define questionnaire
questionnaire = Questionnaire(name="SampleQuestionnaire", version=1)

# Add questions
questionnaire.add_question(
    name="What is your favorite color?",
    type=QuestionType.STRING,
    multiple=True,
    validation_rules=["text"],
    choices=["red", "pink", "blue"],
)
questionnaire.add_question(
    name="How many years of experience do you have in programming?",
    type=QuestionType.INT,
    multiple=True,
    validation_rules=["numeric"],
)

# _questions = [Question(name='What is your favorite color?', type=<QuestionType.STRING: <class 'str'>>, multiple=False, validation_rules=['text']), Question(name='How many years of experience do you have in programming?', type=<QuestionType.INT: <class 'int'>>, multiple=False, validation_rules=['numeric'])]

# Set responses
responses = {
    "How many years of experience do you have in programming?": [2, 3],
    "What is your favorite color?": ["pink", "green"],
    # "interactionID": ["xxx", "yyy"]
}

# Create instance of the QuestionnaireResponseValidator
validator = QuestionnaireResponseValidator(
    questionnaire=questionnaire, responses=responses
)

# Validate and get invalid responses for the questionnaire
invalid_responses = validator.validate_and_get_invalid_responses()
