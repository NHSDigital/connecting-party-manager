from datetime import datetime
from enum import Enum
from uuid import UUID

from .entity import Entity
from .error import DuplicateError


class QuestionType(Enum):
    """
    The data type of the question
    """

    STRING = str
    INT = int
    BOOL = bool
    DATE_TIME = datetime


class Question:
    """
    A single Questionnaire Question
    """

    def __init__(self, name: str, type: QuestionType, multiple: bool):
        self.name = name
        self.type = type
        self.multiple = multiple


class Questionnaire(Entity[UUID]):
    """
    A Questionnaire represents a collection of Questions, in a specific order.
    """

    def __init__(self, id: str, name: str):
        super().__init__(id, name)
        self._questions: list[Question] = []

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
    ):
        """
        Adds a new question to the questionnaire.  Once a questionnaire is
        locked this method will throw an error.
        """
        if name in self:
            raise DuplicateError(f"Question exists: {name}")
        result = Question(name, type=type, multiple=multiple)
        self._questions.append(result)
        return result

    def remove_question(self, name: str):
        """
        Removes a question from the questionnaire.  Once a questionnaire is
        locked this method will throw an error.
        """
        raise NotImplementedError()

    def revise(self) -> "Questionnaire":
        """
        Creates an exact duplicate of the questionnaire, which is the only way
        to edit questionnaires once they become locked.
        """
        raise NotImplemented()
