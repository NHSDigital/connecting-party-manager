from enum import Enum
from typing import List

from .entity import Entity
from .error import DuplicateError


class QuestionType(Enum):
    STRING = "str"
    INT = "int"
    BOOL = "bool"
    DATE_TIME = "datetime"


class Question:
    def __init__(self, name: str, type: QuestionType, multiple: bool):
        self.name = name
        self.type = type
        self.multiple = multiple


class Questionnaire(Entity):
    def __init__(self, id: str, name: str):
        super().__init__(id, name)
        self._questions: List[Question] = []

    def has_question(self, name: str) -> bool:
        return name in [q.name for q in self._questions]

    def add_question(
        self,
        name: str,
        type: QuestionType = QuestionType.STRING,
        multiple: bool = False,
    ):
        if self.has_question(name):
            raise DuplicateError(f"Question exists: {name}")
        result = Question(name, type=type, multiple=multiple)
        self._questions.append(result)
        return result

    def remove_question(self, name: str):
        raise NotImplementedError()
