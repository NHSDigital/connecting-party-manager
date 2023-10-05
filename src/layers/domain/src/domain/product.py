from .error import DuplicateError

from .entity import Entity
from .questionnaire_entity import QuestionnaireEntity


class Product(Entity, QuestionnaireEntity):
    def __init__(
        self,
        id: str,
        name: str,
        questionnaires: Set[str] = None,
        dependency_questionnaires: Set[str] = None,
    ):
        super().__init__(id, name)
        self._questionnaires = (
            set(questionnaires) if questionnaires is not None else set([])
        )
        self._dependency_questionnaires = (
            set(dependency_questionnaires)
            if dependency_questionnaires is not None
            else set([])
        )
