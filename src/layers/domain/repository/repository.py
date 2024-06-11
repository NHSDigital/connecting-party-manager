import sys
from itertools import islice
from typing import TYPE_CHECKING, Generator, Generic, TypeVar

from domain.core.aggregate_root import AggregateRoot

from .transaction import Transaction, TransactItem, handle_client_errors

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient

ModelType = TypeVar("ModelType", bound=AggregateRoot)
T = TypeVar("T")
BATCH_SIZE = 100


def batched(iterable: T, n: int) -> Generator[T, None, None]:
    if sys.version_info >= (3, 12):
        raise RuntimeError(
            f"Replace function '{__file__.__name__}.{batched}' with built-in 'from itertools import batched'"
        )
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))


def _split_transactions_by_key(
    transact_items: list[TransactItem], n_max: int
) -> Generator[list[TransactItem], None, None]:
    buffer, keys = [], set()
    for transact_item in transact_items:
        transaction_statement = transact_item.Put or transact_item.Delete
        item = transaction_statement.Key or transaction_statement.Item
        key = (item["pk"]["S"], item["sk"]["S"])
        if key in keys:
            yield from batched(buffer, n=n_max)
            buffer, keys = [], set()
        buffer.append(transact_item)
        keys.add(key)
    yield from batched(buffer, n=n_max)


class Repository(Generic[ModelType]):
    def __init__(self, table_name, model: type[ModelType], dynamodb_client):
        self.table_name = table_name
        self.model = model
        self.client: "DynamoDBClient" = dynamodb_client

    def write(self, entity: ModelType, batch_size=BATCH_SIZE):
        def generate_transaction_statements(event) -> TransactItem:
            handler_name = f"handle_{type(event).__name__}"
            handler = getattr(self, handler_name)
            return handler(event=event)

        responses = []
        transact_items = map(generate_transaction_statements, entity.events)
        for _transact_items in _split_transactions_by_key(
            transact_items, n_max=batch_size
        ):
            transaction = Transaction(TransactItems=_transact_items)
            with handle_client_errors(commands=_transact_items):
                _response = self.client.transact_write_items(
                    **transaction.dict(exclude_none=True)
                )
                responses.append(_response)
        return responses
