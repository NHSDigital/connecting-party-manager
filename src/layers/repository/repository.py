from typing import Generic, TypeVar

from domain.core.aggregate_root import AggregateRoot
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class Repository(Generic[ModelType]):
    def __init__(self, table_name, model: type[ModelType], dynamodb_client):
        self.table_name = table_name
        self.model = model
        self.client = dynamodb_client

    def write(self, entity: AggregateRoot):
        def execute_event_handler(event):
            handler_name = f"handle_{type(event).__name__}"
            handler = getattr(self, handler_name)
            return handler(event, entity)

        commands = [execute_event_handler(e) for e in entity.events]
        args = {
            "TransactItems": commands,
            "ReturnConsumedCapacity": "NONE",
            "ReturnItemCollectionMetrics": "NONE",
        }
        response = self.client.transact_write_items(**args)
        return response
