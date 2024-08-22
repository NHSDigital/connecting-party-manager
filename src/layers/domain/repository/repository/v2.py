from abc import abstractmethod
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
    from mypy_boto3_dynamodb.type_defs import (
        BatchWriteItemOutputTypeDef,
        TransactWriteItemsOutputTypeDef,
    )

ModelType = TypeVar("ModelType", bound=AggregateRoot)
T = TypeVar("T")
BATCH_SIZE = 100
MAX_BATCH_WRITE_SIZE = 25


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


def transact_write_chunk(
    client: "DynamoDBClient", chunk: list[TransactItem]
) -> "TransactWriteItemsOutputTypeDef":
    transaction = Transaction(TransactItems=chunk)
    with handle_client_errors(commands=chunk):
        _response = client.transact_write_items(**transaction.dict(exclude_none=True))
    return _response


def batch_write_chunk(
    client: "DynamoDBClient", table_name: str, chunk: list[dict]
) -> "BatchWriteItemOutputTypeDef":
    while chunk:
        _response = client.batch_write_item(RequestItems={table_name: chunk})
        chunk = _response["UnprocessedItems"].get(table_name)
    return _response


class Repository(Generic[ModelType]):
    def __init__(self, table_name, model: type[ModelType], dynamodb_client):
        self.table_name = table_name
        self.model = model
        self.client: "DynamoDBClient" = dynamodb_client
        self.batch_size = BATCH_SIZE

    @abstractmethod
    def handle_bulk(self, item):
        ...

    def write(self, entity: ModelType, batch_size=None):
        batch_size = batch_size or self.batch_size

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

        responses = [
            transact_write_chunk(client=self.client, chunk=transact_item_chunk)
            for transact_item_chunk in _split_transactions_by_key(
                transact_items, batch_size
            )
        ]
        return responses

    def write_bulk(self, entities: list[ModelType], batch_size=None):
        batch_size = batch_size or MAX_BATCH_WRITE_SIZE
        batch_write_items = list(chain.from_iterable(map(self.handle_bulk, entities)))
        responses = [
            batch_write_chunk(
                client=self.client, table_name=self.table_name, chunk=chunk
            )
            for chunk in batched(batch_write_items, batch_size)
        ]
        return responses
