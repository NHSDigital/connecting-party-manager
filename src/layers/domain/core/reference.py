from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Reference(BaseModel, Generic[T]):
    """
    When composing an Aggregate Root we do not link directly to other entities,
    but rather include Reference object which contains both computer and human
    identifiers.
    """

    id: T
    name: str
