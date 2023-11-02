from abc import ABC

from .error import DuplicateError, NotFoundError
from .questionnaire import Question, Questionnaire

GLOBAL = "GLOBAL"


class Dataset:
    """
    The data collected by Questionnaires is held in a consolidated bag of
    properties, called a dataset.  Questionnaires may overlap and share the same
    underlying properties, should they wish, or can be completely isolated.
    """

    def __init__(self):
        self._values = []

    def set_values(self, questionnaire: Questionnaire, values: dict[str, any]):
        """
        Provide all the answers for a questionnaire, and store them in the
        dataset.  Each question in the questionnaire will be validated against
        the value provided, and all must pass before the values are written to
        the dataset.
        """
        raise NotImplementedError()

    def validate(self, questionnaire: Questionnaire):
        """
        Validate the current answers in a dataset, to see if they satisfy a
        questionnaire.
        """
        raise NotImplementedError()


class QuestionnaireEntity(ABC):
    """
    A QuestionnaireEntity represents an entity that can store and process
    questionnaire data.  It maintains one ore more DataSet where answers are
    stored.  Each DataSet is given an index key, meaning we can store answers
    to the same questionnaire multiple times but for given index key.  For
    example, we could index by: Global, ODS Code, ASID, Environment.

    At present the ProductTeam and Product are both QuestionnaireEntities, hence
    why this logic is shared here.
    """

    def __init__(self):
        self._datasets = {}

    def add_dataset(self, index: str = GLOBAL) -> Dataset:
        """
        Creates a new dataset and adds it to the collection

        :raises
            DuplicateError: if index entry already exists
        """
        if index in self._datasets:
            raise DuplicateError()

        result = Dataset()
        self._datasets[index] = result
        return result

    def get_dataset(self, index: str = GLOBAL) -> Dataset:
        """
        Returns a single dataset if present, with a more descriptive error
        if not present.

        :raises
            NotFoundError: if index does not exist
        """
        if index not in self._datasets:
            raise NotFoundError(f"Unknown index: {index}")
        return self._datasets[index]

    def get_value(self, name: str, index: str = GLOBAL) -> Question:
        """
        Returns a single value, with a more descriptive error
        if not present
        """

        dataset = self.get_dataset(index)
        if name not in dataset.values[name]:
            raise NotFoundError(f"Unknown value: {index}.{name}")
        return dataset.values[name]
