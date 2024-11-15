import random
import time
from abc import abstractmethod
from enum import StrEnum
from functools import wraps
from itertools import batched, chain
from typing import TYPE_CHECKING, Generator, Iterable

from botocore.exceptions import ClientError
from domain.core.aggregate_root import AggregateRoot
from domain.repository.errors import ItemNotFound
from domain.repository.keys import KEY_SEPARATOR, TableKey
from domain.repository.marshall import marshall, unmarshall
from domain.repository.transaction import (  # TransactItem,
    ConditionExpression,
    Transaction,
    TransactionStatement,
    TransactItem,
    handle_client_errors,
    update_transactions,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient
    from mypy_boto3_dynamodb.type_defs import (
        BatchWriteItemOutputTypeDef,
        TransactWriteItemsOutputTypeDef,
    )

BATCH_SIZE = 100
MAX_BATCH_WRITE_SIZE = 10
RETRY_ERRORS = [
    "ProvisionedThroughputExceededException",
    "ThrottlingException",
    "InternalServerError",
]


class TooManyResults(Exception):
    pass


class QueryType(StrEnum):
    EQUALS = "{} = {}"
    BEGINS_WITH = "begins_with({}, {})"


def exponential_backoff_with_jitter(
    n_retries, base_delay=0.1, min_delay=0.05, max_delay=5
):
    """Calculate the delay with exponential backoff and jitter."""
    delay = min(base_delay * (2**n_retries), max_delay)
    return random.uniform(min_delay, delay)


def retry_with_jitter(max_retries=5, error=ClientError):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            exceptions = []
            while len(exceptions) < max_retries:
                try:
                    return func(*args, **kwargs)
                except error as e:
                    error_code = e.response["Error"]["Code"]
                    if error_code not in RETRY_ERRORS:
                        raise
                    exceptions.append(e)
                delay = exponential_backoff_with_jitter(n_retries=len(exceptions))
                time.sleep(delay)
            raise ExceptionGroup(
                f"Failed to put item after {max_retries} retries", exceptions
            )

        return wrapped

    return wrapper


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


@retry_with_jitter()
def batch_write_chunk(
    client: "DynamoDBClient", table_name: str, chunk: list[dict]
) -> "BatchWriteItemOutputTypeDef":
    while chunk:
        _response = client.batch_write_item(RequestItems={table_name: chunk})
        chunk = _response["UnprocessedItems"].get(table_name)
    return _response


class Repository[ModelType: AggregateRoot]:

    def __init__(
        self,
        table_name,
        model: type[ModelType],
        dynamodb_client,
        parent_table_keys: tuple[TableKey],
        table_key: TableKey,
    ):
        self.table_name = table_name
        self.model = model
        self.client: "DynamoDBClient" = dynamodb_client
        self.batch_size = BATCH_SIZE
        self.parent_table_keys = parent_table_keys
        self.table_key = table_key

    @abstractmethod
    def handle_bulk(self, item): ...

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

    def create_index(
        self,
        id: str,
        parent_key_parts: tuple[str],
        data: dict,
        root: bool,
        table_key: TableKey = None,
        parent_table_keys: tuple[TableKey] = None,
    ) -> TransactItem:
        if table_key is None:
            table_key = self.table_key
        if parent_table_keys is None:
            parent_table_keys = self.parent_table_keys

        if len(parent_table_keys) != len(parent_key_parts):
            raise ValueError(
                f"Expected provide {len(parent_table_keys)} parent key parts, got {len(parent_key_parts)}"
            )

        write_key = table_key.key(id)
        read_key = KEY_SEPARATOR.join(
            table_key.key(_id)
            for table_key, _id in zip(parent_table_keys, parent_key_parts)
        )

        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(
                    pk=write_key,
                    sk=write_key,
                    pk_read=read_key,
                    sk_read=write_key,
                    root=root,
                    **data,
                ),
                ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
            )
        )

    def create_index_batch(
        self,
        id: str,
        parent_key_parts: tuple[str],
        data: dict,
        root: bool,
        table_key: TableKey = None,
        parent_table_keys: tuple[TableKey] = None,
    ) -> TransactItem:
        """
        Difference between `create_index` and `create_index_batch`:

        `create_index` is intended for the event-based
        handlers (e.g. `handle_XyzCreatedEvent`) which are called by the base
        `write` method, which expects `TransactItem`s for use with `client.transact_write_items`

        `create_index_batch` is intended for the entity-based handler
        `handle_bulk` which is called by the base method `write_bulk`, which expects
        `BatchWriteItem`s which we render as a `dict` for use with `client.batch_write_items`
        """

        if table_key is None:
            table_key = self.table_key
        if parent_key_parts is None:
            parent_table_keys = self.parent_table_keys

        write_key = table_key.key(id)
        read_key = KEY_SEPARATOR.join(
            table_key.key(_id)
            for table_key, _id in zip(parent_table_keys, parent_key_parts)
        )

        return {
            "PutRequest": {
                "Item": marshall(
                    pk=write_key,
                    sk=write_key,
                    pk_read=read_key,
                    sk_read=write_key,
                    root=root,
                    **data,
                ),
            },
        }

    def update_indexes(self, id: str, keys: list[str], data: dict):
        primary_keys = [
            marshall(pk=pk, sk=pk) for pk in map(self.table_key.key, [id, *keys])
        ]
        return update_transactions(
            table_name=self.table_name, primary_keys=primary_keys, data=data
        )

    def delete_index(self, id: str):
        pk = self.table_key.key(id)
        return TransactItem(
            Delete=TransactionStatement(
                TableName=self.table_name,
                Key=marshall(pk=pk, sk=pk),
                ConditionExpression=ConditionExpression.MUST_EXIST,
            )
        )

    def _query(self, parent_ids: tuple[str], id: str = None) -> list[ModelType]:
        pk_read = KEY_SEPARATOR.join(
            table_key.key(_id)
            for table_key, _id in zip(self.parent_table_keys, parent_ids)
        )
        sk_read = self.table_key.key(id or "")

        sk_query_type = QueryType.BEGINS_WITH if id is None else QueryType.EQUALS
        sk_condition = sk_query_type.format("sk_read", ":sk_read")

        args = {
            "TableName": self.table_name,
            "IndexName": "idx_gsi_read",
            "KeyConditionExpression": f"pk_read = :pk_read AND {sk_condition}",
            "ExpressionAttributeValues": marshall(
                **{":pk_read": pk_read, ":sk_read": sk_read}
            ),
        }
        result = self.client.query(**args)
        if "LastEvaluatedKey" in result:
            raise TooManyResults(f"Too many results for query ({(*parent_ids, id)})")
        return [self.model(**item) for item in map(unmarshall, result["Items"])]

    def _read(self, parent_ids: tuple[str], id: str) -> ModelType:
        items = self._query(parent_ids=parent_ids or (id,), id=id)
        try:
            (item,) = items
        except ValueError:
            raise ItemNotFound(*parent_ids, id, item_type=self.model)
        return item
