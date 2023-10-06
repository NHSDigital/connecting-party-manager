from abc import ABC


class Entity(ABC):
    """
    Abstract Base Class for handling equality and hashing
    """

    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)
