from attr import asdict, dataclass
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
)
from pydantic import BaseModel, Field


@dataclass
class MyEventAdd:
    field: str


@dataclass
class MyOtherEventAdd:
    field: str


@dataclass
class MyEventDelete:
    field: str


class MyModel(BaseModel):
    field: str
    events: list[MyEventAdd | MyOtherEventAdd | MyEventDelete] = Field(
        default_factory=list, exclude=True
    )

    class Config:
        arbitrary_types_allowed = True


class _NotFoundError(Exception):
    pass


class MyRepositoryMixin:
    def handle_MyEventAdd(self, event: MyEventAdd):
        # This event will raise a transaction error on duplicates
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=event.field, sk=event.field, **asdict(event)),
                ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
            )
        )

    def handle_MyOtherEventAdd(self, event: MyOtherEventAdd):
        # This event will never raise a transaction error
        key = "prefix:" + event.field
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=key, sk=key, **asdict(event)),
            )
        )

    def handle_MyEventDelete(self, event: MyEventDelete):
        # This event will never raise a transaction error
        key = event.field
        return TransactItem(
            Delete=TransactionStatement(
                TableName=self.table_name,
                Key=marshall(pk=key, sk=key),
                ConditionExpression=ConditionExpression.MUST_EXIST,
            )
        )

    def read(self, pk) -> MyModel:
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk",
            "ExpressionAttributeValues": {":pk": marshall_value(pk)},
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise _NotFoundError()
        return MyModel(**items[0])
