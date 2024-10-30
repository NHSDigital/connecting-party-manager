from typing import Generic, List, TypeVar

from domain.core.aggregate_root import AggregateRoot

T = TypeVar("T", bound=AggregateRoot)


class SearchResponse(Generic[T], AggregateRoot):
    results: List[T]

    @classmethod
    def from_models(cls, models: List[T]) -> "SearchResponse[T]":
        return cls(results=models)
