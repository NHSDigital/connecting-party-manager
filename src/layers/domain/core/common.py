from typing import Iterable, TypeVar

SetType = TypeVar("SetType")


def default_set(iterable: Iterable[SetType]) -> set[SetType]:
    """
    Solve the problem of default parameters being shared references in Python
    """
    return set(iterable if iterable is not None else [])


ListType = TypeVar("ListType")


def default_list(iterable) -> list[ListType]:
    """
    Solve the problem of default parameters being shared references in Python
    """
    return list(iterable if iterable is not None else [])
