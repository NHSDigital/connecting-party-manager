from typing import TypeVar
from uuid import UUID

from .common import default_set
from .entity import Entity
from .questionnaire_entity import QuestionnaireEntity

T = TypeVar("T")


class Product(Entity[UUID], QuestionnaireEntity):
    """
    A Product represents logical and physical software products.  A Product may
    be referenced by multiple keys, such as internal GUID, Product Id, ASID,
    etc.
    """

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
