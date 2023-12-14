from typing import Generic, TypeVar

from domain.core.aggregate_root import AggregateRoot

from .transaction import Transaction, TransactionItem, handle_client_errors

ModelType = TypeVar("ModelType", bound=AggregateRoot)


class Repository(Generic[ModelType]):
    def __init__(self, table_name, model: type[ModelType], dynamodb_client):
        self.table_name = table_name
        self.model = model
        self.client = dynamodb_client

    def write(self, entity: ModelType):
        def generate_transaction_statements(event) -> TransactionItem:
            handler_name = f"handle_{type(event).__name__}"
            handler = getattr(self, handler_name)
            return handler(event=event, entity=entity)

        transact_items = list(map(generate_transaction_statements, entity.events))
        transaction = Transaction(TransactItems=transact_items)
        with handle_client_errors(commands=transaction.TransactItems):
            response = self.client.transact_write_items(
                **transaction.dict(exclude_none=True)
            )
        return response
