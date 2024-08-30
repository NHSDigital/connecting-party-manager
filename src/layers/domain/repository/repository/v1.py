from itertools import batched
from typing import TYPE_CHECKING

from domain.core.aggregate_root import AggregateRoot
from domain.repository.transaction import (
    Transaction,
    TransactItem,
    handle_client_errors,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient

BATCH_SIZE = 100


class Repository[ModelType: AggregateRoot]:
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
        for events in batched(entity.events, n=batch_size):
            transact_items = list(map(generate_transaction_statements, events))
            transaction = Transaction(TransactItems=transact_items)

            with handle_client_errors(commands=transact_items):
                _response = self.client.transact_write_items(
                    **transaction.dict(exclude_none=True)
                )
                responses.append(_response)
        return responses
