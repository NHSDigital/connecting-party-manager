from typing import Generic, TypeVar

from .reference import Reference

T = TypeVar("T")


class Entity(Generic[T]):
    """
    Abstract Base Class for handling equality and hashing
    """

    def __init__(self, id: T, name: str):
        assert name.strip() != "", "Invalid name"
        self.id = id
        self.name = name.strip()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def as_reference(self) -> Reference:
        return Reference(type(self).__name__, self.id, self.name)
