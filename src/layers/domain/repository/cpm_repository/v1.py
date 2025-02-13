from enum import StrEnum
from itertools import batched, chain
from typing import TYPE_CHECKING, Generator, Iterable

from domain.core.aggregate_root import AggregateRoot
from domain.core.enum import EntityType
from domain.repository.errors import ItemNotFound
from domain.repository.keys import KEY_SEPARATOR, TableKey
from domain.repository.marshall import marshall, unmarshall
from domain.repository.transaction import (
    ConditionExpression,
    Transaction,
    TransactionStatement,
    TransactItem,
    handle_client_errors,
    update_transactions,
)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBClient
    from mypy_boto3_dynamodb.type_defs import TransactWriteItemsOutputTypeDef

BATCH_SIZE = 100


class TooManyResults(Exception):
    pass


class QueryType(StrEnum):
    EQUALS = "{} = {}"
    BEGINS_WITH = "begins_with({}, {})"


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

    def create_index(
        self,
        id: str,
        parent_key_parts: tuple[str],
        data: dict,
        root: bool,
        row_type: str,
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

        sort_key = table_key.key(id)
        partition_key = KEY_SEPARATOR.join(
            table_key.key(_id)
            for table_key, _id in zip(parent_table_keys, parent_key_parts)
        )

        item_data = {
            "pk": partition_key,
            "sk": sort_key,
            "pk_read_1": sort_key,
            "sk_read_1": sort_key,
            "root": root,
            "row_type": row_type,
            **data,
        }

        if row_type != EntityType.PRODUCT_TEAM_ALIAS:
            item_data["pk_read_2"] = TableKey.ORG_CODE.key(data["ods_code"])
            item_data["sk_read_2"] = sort_key

        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(**item_data),
                ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
            )
        )

    def update_indexes(self, pk: str, id: str, keys: list[str], data: dict):
        primary_keys = [
            marshall(pk=pk, sk=sk) for sk in map(self.table_key.key, [id, *keys])
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

    def _query(
        self, parent_ids: tuple[str], id: str = None, status: str = "all"
    ) -> list[dict]:
        pk = KEY_SEPARATOR.join(
            table_key.key(_id)
            for table_key, _id in zip(self.parent_table_keys, parent_ids)
        )
        sk = self.table_key.key(id or "")

        sk_query_type = QueryType.BEGINS_WITH if id is None else QueryType.EQUALS
        sk_condition = sk_query_type.format("sk", ":sk")
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": f"pk = :pk AND {sk_condition}",
            "ExpressionAttributeValues": marshall(**{":pk": pk, ":sk": sk}),
        }
        if status != "all":
            args["FilterExpression"] = "#status = :status"
            args["ExpressionAttributeValues"][":status"] = {"S": status}
            # status is a reserved keyword so we need to alias it.
            args["ExpressionAttributeNames"] = {"#status": "status"}
        result = self.client.query(**args)
        if "LastEvaluatedKey" in result:
            raise TooManyResults(f"Too many results for query ({(*parent_ids, id)})")
        return list(map(unmarshall, result["Items"]))

    def _search(self, parent_ids: tuple[str]) -> list[ModelType]:
        return [
            self.model(**item)
            for item in self._query(parent_ids=parent_ids)
            if item.get("root") is True
        ]

    def _read(self, parent_ids: tuple[str], id: str, status: str = "all") -> ModelType:
        items = self._query(parent_ids=parent_ids or (id,), id=id, status=status)
        try:
            (item,) = items
        except ValueError:
            if id in parent_ids:
                raise ItemNotFound(id, item_type=self.model)
            raise ItemNotFound(*filter(bool, parent_ids), id, item_type=self.model)
        return self.model(**item)
