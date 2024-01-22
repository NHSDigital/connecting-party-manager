from datetime import datetime
from enum import Enum

from domain.core.error import DuplicateError, InvalidResponseError
from domain.core.validation import ENTITY_NAME_REGEX
from pydantic import BaseModel, Field, ValidationError


class QuestionType(Enum):
    """
    The data type of the question
    """

    STRING = str
    INT = int
    BOOL = bool
    DATE_TIME = datetime
    # ADD OTHER TYPES


class Question(BaseModel):
    """
    A single Questionnaire Question
    """

    name: str
    type: QuestionType
    multiple: bool
    validation_rules: list[str] = []


class Questionnaire(BaseModel):
    """
    A Questionnaire represents a collection of Questions, in a specific order.
    """

    name: str = Field(regex=ENTITY_NAME_REGEX)
    version: int
    _questions: list[
        Question
    ] = []  # Change to dict of question name mapping onto question?

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
    ):
        """
        Adds a new question to the questionnaire.  Once a questionnaire is
        locked this method will throw an error.
        """
        if name in self:
            raise DuplicateError(f"Question exists: {name}")
        result = Question(
            name=name, type=type, multiple=multiple, validation_rules=validation_rules
        )
        self._questions.append(result)
        return result

    # def remove_question(self, name: str):
    #     """
    #     Removes a question from the questionnaire.  Once a questionnaire is
    #     locked this method will throw an error.
    #     """
    #     raise NotImplementedError()

    # def revise(self) -> "Questionnaire":
    #     """
    #     Creates an exact duplicate of the questionnaire, which is the only way
    #     to edit questionnaires once they become locked.
    #     """
    #     raise NotImplementedError()


# How to check multiple answers given or not?


class QuestionnaireResponse(BaseModel):
    """
    Represents a Questionnaire response mapping Questions to Responses.
    """

    responses: dict


class QuestionnaireResponseValidator(BaseModel):
    questionnaire: Questionnaire
    responses: dict

    def validate_response_type(self, question_name, response):
        question = next(
            (q for q in self.questionnaire._questions if q.name == question_name), {}
        )
        question_type = question.type
        # Check if the response is of the correct type
        if not isinstance(response, question.type.value):
            return False, question_type

        return True, None

    def validate_questionnaire_responses_type(self):
        invalid_response_types = []
        for question_name, response in self.responses.items():
            is_valid, failed_type = self.validate_response_type(question_name, response)

            if not is_valid:
                invalid_response_types.append((question_name, response, failed_type))

        return invalid_response_types

    def validate_question_response(self, question_name, response):
        question = next(
            (q for q in self.questionnaire._questions if q.name == question_name), {}
        )

        validation_rules = question.validation_rules

        for validation_rule in validation_rules:
            if validation_rule == "text":
                if not (isinstance(response, str) and len(response) > 0):
                    return (
                        False,
                        validation_rule,
                    )  # Returns at first failed rule only - not showing all failed criteria
            # Add more validation criteria for different question types as needed

        return True, None  # All validation rules passed

    def validate_questionnaire_responses(self):
        invalid_responses = []
        for question_name, response in self.responses.items():
            is_valid, failed_rule = self.validate_question_response(
                question_name, response
            )

            if not is_valid:
                invalid_responses.append((question_name, response, failed_rule))

        return invalid_responses

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
                    f"Invalid response: {question_name} is not a valid question in the questionnaire: {self.questionnaire.name}."
                )  # should this message be different? Wrong questionnaire answered?

        invalid_response_types = self.validate_questionnaire_responses_type()
        invalid_responses = self.validate_questionnaire_responses()

        if not invalid_response_types and not invalid_responses:
            # print("\nAll responses are valid.") -- doesn't indicate that all valid, that needed?
            return invalid_response_types, invalid_responses

        else:
            failed_validation_types_explained = []
            failed_validation_explained = []
            for question_name, response, failed_type in invalid_response_types:
                failed_validation_type = f"Question '{question_name}': {response} (Failed validation type: {failed_type})"
                failed_validation_types_explained.append(failed_validation_type)

            for question_name, response, validation_rule in invalid_responses:
                failed_validation = f"Question '{question_name}': {response} (Failed validation for rule: {validation_rule})"
                failed_validation_explained.append(failed_validation)

            if failed_validation_explained == []:
                raise InvalidResponseError(
                    f"Invalid response types: {failed_validation_types_explained}"
                )

            if failed_validation_types_explained == []:
                raise InvalidResponseError(
                    f"Invalid responses given: {failed_validation_explained}"
                )

            raise InvalidResponseError(
                f"Invalid response types: {failed_validation_types_explained}. Invalid responses given: {failed_validation_explained}"
            )
        return invalid_response_types, invalid_responses


# Example Usage:

# Define questionnaire
questionnaire = Questionnaire(name="SampleQuestionnaire", version=1)

# Add questions
questionnaire.add_question(
    name="What is your favorite color?",
    type=QuestionType.STRING,
    multiple=False,
    validation_rules=["text"],
)
questionnaire.add_question(
    name="How many years of experience do you have in programming?",
    type=QuestionType.INT,
    multiple=False,
    validation_rules=["numeric"],
)

# _questions = [Question(name='What is your favorite color?', type=<QuestionType.STRING: <class 'str'>>, multiple=False, validation_rules=['text']), Question(name='How many years of experience do you have in programming?', type=<QuestionType.INT: <class 'int'>>, multiple=False, validation_rules=['numeric'])]

# Set responses
responses = {
    "How many years of experience do you have in programming?": "2",
    "What is your favorite color?": 2,
}

# Create instance of the QuestionnaireResponseValidator
validator = QuestionnaireResponseValidator(
    questionnaire=questionnaire, responses=responses
)

# Validate and get invalid responses for the questionnaire
invalid_responses = validator.validate_and_get_invalid_responses()
