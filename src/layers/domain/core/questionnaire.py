from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from .error import DuplicateError, InvalidResponseError
from .validation import ENTITY_NAME_REGEX


class QuestionType(Enum):
    """
    The data type of the question
    """

    STRING = str
    INT = int
    BOOL = bool
    DATE_TIME = datetime


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

    id: UUID
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
    ):
        """
        Adds a new question to the questionnaire.  Once a questionnaire is
        locked this method will throw an error.
        """
        if name in self:
            raise DuplicateError(f"Question exists: {name}")
        result = Question(name=name, type=type, multiple=multiple, validation_rules=validation_rules)
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
    
# Needs to check type first then check validation rules? Put type as a validation rule?
    # How to check multiple answers given or not?
class questionnaire_response_validator:
    def __init__(self, questionnaire):
        self.questionnaire = questionnaire
    
    def validate_question_response(self, question_name, response):
        # Add your specific criteria for response format validation based on the question
        question = next((q for q in self.questionnaire if q["name"] == question_name), {})
        validation_rules = question.get("validation_rules", [])

        for validation_rule in validation_rules:
            if validation_rule == "text":
                if not (isinstance(response, str) and len(response) > 0):
                    return False, validation_rule # Returns at first failed rule only - not showing all failed criteria
            elif validation_rule == "numeric":
                if not response.isdigit():
                    return False, validation_rule
            # Add more validation criteria for different question types as needed
                
        return True, None # All validation rules passed
    
    def validate_questionnaire_responses(self, questionnaire_responses):
        invalid_responses = []
        for question_name, response in questionnaire_responses.items():
            is_valid, failed_rule = self.validate_question_response(question_name, response)

            if not is_valid:
                invalid_responses.append((question_name, response, failed_rule))

        return invalid_responses

    def validate_and_get_invalid_responses(self, questionnaire_responses):
        invalid_responses = self.validate_questionnaire_responses(questionnaire_responses)

        if not invalid_responses:
            print("\nAll responses are valid.")
        else:
            failed_validation_explained = []
            for question_name, response, validation_rule in invalid_responses:
                failed_validation = (f"Question '{question_name}': {response} (Failed validation for rule: {validation_rule})")
                failed_validation_explained.append(failed_validation)
            raise InvalidResponseError(f"Invalid response given: {failed_validation_explained}") 
        return invalid_responses
    
# Need to check questionnaire responses are for right questionnaire?
# - Validation passes if different questions are answered as to what is in questionnaire


# Example Usage:

# Define your questionnaire with validation rules and questions
questionnaire1 = [
    {"name": "What is your favorite color?", "validation_rules": ["text"]},
    {"name": "How many years of experience do you have in programming?", "validation_rules": ["text", "numeric"]},
    # Add more questions as needed with different types
]

# Example user responses
user_responses1 = {
    "How many years of experience do you have in programming?": "five",
    "What is your favorite color?": 5,
    # Add more responses as needed
}

# Create instance of the questionnaire_response_validator
validator1 = questionnaire_response_validator(questionnaire1)

# Validate and get invalid responses for the questionnaire
invalid_responses1 = validator1.validate_and_get_invalid_responses(user_responses1)

