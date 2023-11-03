from typing import Generic, TypeVar

from domain.core.validation import validate_entity_name

T = TypeVar("T")


class Entity(Generic[T]):
    """
    Abstract Base Class for handling equality and hashing
    """

    def __init__(self, id: T, name: str):
        validate_entity_name(name)

        self.id = id
        self.name = name.strip()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id
