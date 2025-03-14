from enum import StrEnum

from attr import asdict, dataclass
from domain.repository.cpm_repository import Repository
from domain.repository.keys import TableKeyAction
from domain.repository.marshall import marshall
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
)
from pydantic import BaseModel, Field

from conftest import dynamodb_client_with_sleep as dynamodb_client
from test_helpers.terraform import read_terraform_output


class MyTableKey(TableKeyAction, StrEnum):
    FOO = "foo"
    BAR = "bar"


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


class MyRepository(Repository[MyModel]):
    def __init__(self):
        table_name = read_terraform_output("dynamodb_cpm_table_name.value")
        super().__init__(
            table_name=table_name,
            model=MyModel,
            dynamodb_client=dynamodb_client(),
            parent_table_keys=(MyTableKey.FOO,),
            table_key=MyTableKey.FOO,
        )

    def read(self, id: str):
        return self._read(parent_ids=(id,), id=id)

    def handle_bulk(self, item):
        return [{"PutRequest": {"Item": marshall(**item)}}]

    def handle_MyEventAdd(self, event: MyEventAdd):
        # This event will raise a transaction error on duplicates
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(
                    pk=MyTableKey.FOO.key(event.field),
                    sk=MyTableKey.FOO.key(event.field),
                    pk_read_1=MyTableKey.FOO.key(event.field),
                    sk_read_1=MyTableKey.FOO.key(event.field),
                    pk_read_2=MyTableKey.FOO.key(event.field),
                    sk_read_2=MyTableKey.FOO.key(event.field),
                    **asdict(event)
                ),
                ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
            )
        )

    def handle_MyOtherEventAdd(self, event: MyOtherEventAdd):
        return TransactItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(
                    pk=MyTableKey.BAR.key(event.field),
                    sk=MyTableKey.BAR.key(event.field),
                    pk_read_1=MyTableKey.BAR.key(event.field),
                    sk_read_1=MyTableKey.BAR.key(event.field),
                    pk_read_2=MyTableKey.BAR.key(event.field),
                    sk_read_2=MyTableKey.BAR.key(event.field),
                    **asdict(event)
                ),
            )
        )

    def handle_MyEventDelete(self, event: MyEventDelete):
        return TransactItem(
            Delete=TransactionStatement(
                TableName=self.table_name,
                Key=marshall(
                    pk=MyTableKey.FOO.key(event.field),
                    sk=MyTableKey.FOO.key(event.field),
                ),
                ConditionExpression=ConditionExpression.MUST_EXIST,
            )
        )
