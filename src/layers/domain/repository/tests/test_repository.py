import pytest
from attr import asdict, dataclass
from domain.repository.errors import AlreadyExistsError
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository import Repository
from domain.repository.transaction import (
    ConditionExpression,
    TransactionStatement,
    TransactItem,
)
from event.aws.client import dynamodb_client
from pydantic import BaseModel, Field

from test_helpers.terraform import read_terraform_output


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


@pytest.fixture
def repository() -> "MyRepository":
    table_name = read_terraform_output("dynamodb_table_name.value")
    return MyRepository(
        table_name=table_name,
        model=MyModel,
        dynamodb_client=dynamodb_client(),
    )


class _NotFoundError(Exception):
    pass


class MyRepository(Repository[MyModel]):
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


@pytest.mark.integration
def test_repository_write(repository: MyRepository):
    value = "123"
    my_item = MyModel(field=value, events=[MyEventAdd(field=value)])
    repository.write(my_item)
    assert repository.read(pk=value).dict() == my_item.dict()


@pytest.mark.integration
def test_repository_raise_already_exists(repository: MyRepository):
    my_item = MyModel(field="123", events=[MyEventAdd(field="123")])
    repository.write(my_item)
    with pytest.raises(AlreadyExistsError):
        repository.write(my_item)


@pytest.mark.integration
def test_repository_raise_already_exists_multiple_events(repository: MyRepository):
    my_item = MyModel(
        field="123",
        events=[
            MyOtherEventAdd(field="456"),
            MyEventAdd(field="123"),
            MyOtherEventAdd(field="345"),
        ],
    )
    repository.write(my_item)
    with pytest.raises(AlreadyExistsError):
        repository.write(my_item)  # Should cause AlreadyExistsError


@pytest.mark.integration
def test_repository_raise_already_exists_from_single_transaction(
    repository: MyRepository,
):
    my_item = MyModel(
        field="123",
        events=[
            MyOtherEventAdd(field="456"),
            MyEventAdd(field="123"),
            MyOtherEventAdd(field="345"),
            MyEventAdd(field="123"),
        ],
    )
    with pytest.raises(AlreadyExistsError) as exc:
        repository.write(my_item)
    assert str(exc.value) == "Item already exists"


@pytest.mark.integration
def test_repository_add_and_delete_separate_transactions(repository: MyRepository):
    value = "123"
    my_item = MyModel(field=value, events=[MyEventAdd(field=value)])
    repository.write(my_item)
    intermediate_item = repository.read(pk=value)

    assert intermediate_item == my_item

    intermediate_item.events.append(MyEventDelete(field=value))
    repository.write(intermediate_item)

    with pytest.raises(_NotFoundError):
        repository.read(pk=value)
