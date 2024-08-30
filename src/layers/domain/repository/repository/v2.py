import random
import time
from abc import abstractmethod
from functools import wraps
from itertools import batched, chain
from typing import TYPE_CHECKING, Generator, Iterable

from botocore.exceptions import ClientError
from domain.core.aggregate_root import AggregateRoot
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

BATCH_SIZE = 100
MAX_BATCH_WRITE_SIZE = 10
RETRY_ERRORS = [
    "ProvisionedThroughputExceededException",
    "ThrottlingException",
    "InternalServerError",
]


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
    def __init__(self, table_name, model: type[ModelType], dynamodb_client):
        self.table_name = table_name
        self.model = model
        self.client: "DynamoDBClient" = dynamodb_client
        self.batch_size = BATCH_SIZE

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
