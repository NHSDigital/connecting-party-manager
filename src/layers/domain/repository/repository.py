import sys
from itertools import islice
from typing import TYPE_CHECKING, Generator, Generic, TypeVar

from domain.core.aggregate_root import AggregateRoot

from .transaction import Transaction, handle_client_errors

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


class Repository(Generic[ModelType]):
    def __init__(self, table_name, model: type[ModelType], dynamodb_client):
        self.table_name = table_name
        self.model = model
        self.client: "DynamoDBClient" = dynamodb_client

    def write(self, entity: ModelType, batch_size=BATCH_SIZE):
        def generate_transaction_statements(event):
            handler_name = f"handle_{type(event).__name__}"
            handler = getattr(self, handler_name)
            # print("handler_name", handler_name)
            return handler(event=event)

        responses = []
        for events in batched(entity.events, n=batch_size):
            for event in events:
                transact_items = generate_transaction_statements(event)

                #  either a list or a single
                if not isinstance(transact_items, list):
                    transact_items = [transact_items]

                # print("transact_items", transact_items)
                transaction = Transaction(TransactItems=transact_items)

                with handle_client_errors(commands=transact_items):
                    _response = self.client.transact_write_items(
                        **transaction.dict(exclude_none=True)
                    )
                    responses.append(_response)
        return responses
