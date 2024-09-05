from abc import abstractmethod
from itertools import chain
from typing import Generic

from domain.repository.errors import ItemNotFound
from domain.repository.marshall import marshall, unmarshall
from domain.repository.repository.v1 import batched
from domain.repository.repository.v2 import (
    BATCH_SIZE,
    MAX_BATCH_WRITE_SIZE,
    ModelType,
    _split_transactions_by_key,
    batch_write_chunk,
    transact_write_chunk,
)
from mypy_boto3_dynamodb import DynamoDBClient


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

    def read(self, key_type: str) -> int:
        """
        Read the table by pk, sk
        """

        result = self.client.get_item(
            TableName=self.table_name, Key=marshall(pk=key_type, sk=key_type)
        )
        try:
            item = result["Item"]
        except KeyError:
            raise ItemNotFound(key_type)

        entry = unmarshall(item)
        return entry
