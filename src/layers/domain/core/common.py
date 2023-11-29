from typing import Iterable, TypeVar

T = TypeVar("T")


def default_set(iterable: Iterable[T]) -> set[T]:
    """
    Solve the problem of default parameters being shared references in Python
    """
    return set(iterable if iterable is not None else [])


def default_list(iterable: Iterable[T]) -> list[T]:
    """
    Solve the problem of default parameters being shared references in Python
    """
    return list(iterable if iterable is not None else [])
