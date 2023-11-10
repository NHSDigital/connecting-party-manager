from typing import Generic, TypeVar

import boto3
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class Repository(Generic[ModelType]):
    def __init__(self, table_name, model: type[ModelType]):
        self.table_name = table_name
        self.model = model
        self.client = boto3.client("dynamodb")

    def write(self, entity):
        def get_handler_name(event):
            handler_name = f"handle_{type(event).__name__}"
            handler = getattr(self, handler_name)
            return handler(event, entity)

        commands = [get_handler_name(e) for e in entity.events]
        args = {
            "TransactItems": commands,
            "ReturnConsumedCapacity": "NONE",
            "ReturnItemCollectionMetrics": "NONE",
        }
        response = self.client.transact_write_items(**args)
        return response

    def register(self, event: type, handler):
        self.handlers[event.__name__] = handler
