import pytest
from domain.repository.errors import AlreadyExistsError, UnhandledTransaction
from domain.repository.repository import Repository
from event.aws.client import dynamodb_client

from test_helpers.terraform import read_terraform_output

from .model import (
    MyEventAdd,
    MyEventDelete,
    MyModel,
    MyOtherEventAdd,
    MyRepositoryMixin,
    _NotFoundError,
)


@pytest.fixture
def repository() -> "MyRepository":
    table_name = read_terraform_output("dynamodb_table_name.value")
    return MyRepository(
        table_name=table_name,
        model=MyModel,
        dynamodb_client=dynamodb_client(),
    )


class MyRepository(Repository[MyModel], MyRepositoryMixin):
    pass


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
    with pytest.raises(UnhandledTransaction) as exc:
        repository.write(my_item)
    assert str(exc.value) == "\n".join(
        (
            "ValidationException: Transaction request cannot include multiple operations on one item",
            f'{{"Put": {{"TableName": "{repository.table_name}", "Item": {{"pk": {{"S": "prefix:456"}}, "sk": {{"S": "prefix:456"}}, "field": {{"S": "456"}}}}}}}}',
            f'{{"Put": {{"TableName": "{repository.table_name}", "Item": {{"pk": {{"S": "123"}}, "sk": {{"S": "123"}}, "field": {{"S": "123"}}}}, "ConditionExpression": "attribute_not_exists(pk)"}}}}',
            f'{{"Put": {{"TableName": "{repository.table_name}", "Item": {{"pk": {{"S": "prefix:345"}}, "sk": {{"S": "prefix:345"}}, "field": {{"S": "345"}}}}}}}}',
            f'{{"Put": {{"TableName": "{repository.table_name}", "Item": {{"pk": {{"S": "123"}}, "sk": {{"S": "123"}}, "field": {{"S": "123"}}}}, "ConditionExpression": "attribute_not_exists(pk)"}}}}',
        )
    )


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
