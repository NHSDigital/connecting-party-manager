from dataclasses import asdict, dataclass

import pytest
from domain.repository.errors import AlreadyExistsError, UnhandledTransaction
from domain.repository.marshall import marshall, marshall_value, unmarshall
from domain.repository.repository import Repository
from domain.repository.transaction import (
    ConditionExpression,
    TransactionItem,
    TransactionStatement,
)
from event.aws.client import dynamodb_client
from pydantic import BaseModel, Field

from test_helpers.terraform import read_terraform_output


@dataclass
class MyEvent:
    field: str


@dataclass
class MyOtherEvent:
    field: str


class MyModel(BaseModel):
    field: str
    events: list[MyEvent | MyOtherEvent] = Field(default_factory=list, exclude=True)


class MyRepository(Repository[MyModel]):
    def handle_MyEvent(self, event: MyEvent, entity: MyModel):
        # This event will raise a transaction error on duplicates
        return TransactionItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=event.field, sk=event.field, **asdict(event)),
                ConditionExpression=ConditionExpression.MUST_NOT_EXIST,
            )
        )

    def handle_MyOtherEvent(self, event: MyEvent, entity: MyModel):
        # This event will never raise a transaction error
        key = "prefix:" + event.field
        return TransactionItem(
            Put=TransactionStatement(
                TableName=self.table_name,
                Item=marshall(pk=key, sk=key, **asdict(event)),
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
        return MyModel(**items[0])


@pytest.mark.integration
def test_repository():
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = MyRepository(
        table_name=table_name,
        model=MyModel,
        dynamodb_client=dynamodb_client(),
    )

    value = "123"
    my_item = MyModel(field=value, events=[MyEvent(field=value)])
    repo.write(my_item)
    assert repo.read(pk=value).dict() == my_item.dict()


@pytest.mark.integration
def test_repository_raise_already_exists():
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = MyRepository(
        table_name=table_name,
        model=MyModel,
        dynamodb_client=dynamodb_client(),
    )

    my_item = MyModel(field="123", events=[MyEvent(field="123")])
    repo.write(my_item)
    with pytest.raises(AlreadyExistsError):
        repo.write(my_item)


@pytest.mark.integration
def test_repository_raise_already_exists_multiple_events():
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = MyRepository(
        table_name=table_name,
        model=MyModel,
        dynamodb_client=dynamodb_client(),
    )

    my_item = MyModel(
        field="123",
        events=[
            MyOtherEvent(field="456"),
            MyEvent(field="123"),
            MyOtherEvent(field="345"),
        ],
    )
    repo.write(my_item)
    with pytest.raises(AlreadyExistsError):
        repo.write(my_item)  # Should cause AlreadyExistsError


@pytest.mark.integration
def test_repository_raise_already_exists_from_single_transaction():
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = MyRepository(
        table_name=table_name,
        model=MyModel,
        dynamodb_client=dynamodb_client(),
    )

    my_item = MyModel(
        field="123",
        events=[
            MyOtherEvent(field="456"),
            MyEvent(field="123"),
            MyOtherEvent(field="345"),
            MyEvent(field="123"),
        ],
    )
    with pytest.raises(UnhandledTransaction) as exc:
        repo.write(my_item)
    assert str(exc.value) == "\n".join(
        (
            "ValidationException: Transaction request cannot include multiple operations on one item",
            f'{{"Put": {{"TableName": "{table_name}", "Item": {{"pk": {{"S": "prefix:456"}}, "sk": {{"S": "prefix:456"}}, "field": {{"S": "456"}}}}, "ConditionExpression": null}}}}',
            f'{{"Put": {{"TableName": "{table_name}", "Item": {{"pk": {{"S": "123"}}, "sk": {{"S": "123"}}, "field": {{"S": "123"}}}}, "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk) AND attribute_not_exists(pk_1) AND attribute_not_exists(sk_1) AND attribute_not_exists(pk_2) AND attribute_not_exists(sk_2)"}}}}',
            f'{{"Put": {{"TableName": "{table_name}", "Item": {{"pk": {{"S": "prefix:345"}}, "sk": {{"S": "prefix:345"}}, "field": {{"S": "345"}}}}, "ConditionExpression": null}}}}',
            f'{{"Put": {{"TableName": "{table_name}", "Item": {{"pk": {{"S": "123"}}, "sk": {{"S": "123"}}, "field": {{"S": "123"}}}}, "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk) AND attribute_not_exists(pk_1) AND attribute_not_exists(sk_1) AND attribute_not_exists(pk_2) AND attribute_not_exists(sk_2)"}}}}',
        )
    )
