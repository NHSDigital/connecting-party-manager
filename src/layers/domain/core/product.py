from typing import Iterable, TypeVar

from .entity import Entity
from .questionnaire_entity import QuestionnaireEntity

T = TypeVar("T")


def default_set(iterable: Iterable[T]) -> set[T]:
    return set(iterable if iterable is not None else [])


class Product(Entity, QuestionnaireEntity):
    def __init__(
        self,
        id: str,
        name: str,
        questionnaires: set[str] = None,
        dependency_questionnaires: set[str] = None,
    ):
        super().__init__(id, name)
        self._questionnaires = default_set(questionnaires)
        self._dependency_questionnaires = default_set(dependency_questionnaires)
