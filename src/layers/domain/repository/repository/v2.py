from itertools import chain
from typing import TYPE_CHECKING, Generator, Generic, Iterable, TypeVar

from domain.core.aggregate_root import AggregateRoot
from domain.repository.repository.v1 import batched
from domain.repository.transaction import (  # TransactItem,
    Transaction,
    TransactItem,
    handle_client_errors,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient

ModelType = TypeVar("ModelType", bound=AggregateRoot)
T = TypeVar("T")
BATCH_SIZE = 100


def _split_transactions_by_key(
    transact_items: Iterable[TransactItem], n_max: int
) -> Generator[list[TransactItem], None, None]:
    buffer, keys = [], set()
    for transact_item in transact_items:
        transaction_statement = (
            transact_item.Put or transact_item.Delete or transact_item.Update
        )
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
        def generate_transaction_statements(event):
            handler_name = f"handle_{type(event).__name__}"
            handler = getattr(self, handler_name)
            transact_items = handler(event=event)
            if not isinstance(transact_items, list):
                transact_items = [transact_items]
            return transact_items

        transact_items = chain.from_iterable(
            (generate_transaction_statements(event) for event in entity.events)
        )

        responses = []
        for transact_item_chunk in _split_transactions_by_key(
            transact_items, batch_size
        ):
            transaction = Transaction(TransactItems=transact_item_chunk)
            with handle_client_errors(commands=transact_item_chunk):
                _response = self.client.transact_write_items(
                    **transaction.dict(exclude_none=True)
                )
                responses.append(_response)
        return responses
