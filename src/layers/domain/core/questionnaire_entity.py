from abc import ABC

from .error import DuplicateError, NotFoundError
from .questionnaire import Question, Questionnaire


class Dataset:
    def __init__(self):
        self._values = []

    def set_values(self, questionnaire: Questionnaire, values: dict[str, any]):
        raise NotImplementedError()

    def validate(self, questionnaire: Questionnaire):
        raise NotImplementedError()


class QuestionnaireEntity(ABC):
    def __init__(self):
        self._datasets = {}

    def add_dataset(self, index: str) -> Dataset:
        """
        Creates a new dataset and adds it to the collection

        :raises
            DuplicateError: if index already exists
        """
        if index in self._datasets:
            raise DuplicateError()

        result = Dataset()
        self._datasets[index] = result
        return result

    def get_dataset(self, index: str) -> Dataset:
        """
        Returns a single dataset if present, with a more descriptive error
        if not present.

        :raises
            NotFoundError: if index does not exist
        """
        if index not in self._datasets:
            raise NotFoundError(f"Unknown index: {index}")
        return self._datasets[index]

    def get_value(self, index: str, name: str) -> Question:
        """
        Returns a single value, with a more descriptive error
        if not present
        """

        dataset = self.get_dataset(index)
        if name not in dataset.values[name]:
            raise NotFoundError(f"Unknown value: {index}.{name}")
        return dataset.values[name]
