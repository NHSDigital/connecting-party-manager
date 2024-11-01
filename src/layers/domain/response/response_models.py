from domain.core.aggregate_root import AggregateRoot


class SearchResponse[T](AggregateRoot):
    results: list[T]
