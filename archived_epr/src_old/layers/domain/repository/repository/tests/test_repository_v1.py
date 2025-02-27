import pytest
from domain.repository.errors import AlreadyExistsError, ItemNotFound

from .model_v1 import MyEventAdd, MyEventDelete, MyModel, MyOtherEventAdd, MyRepository


@pytest.fixture
def repository() -> "MyRepository":
    return MyRepository()


@pytest.mark.integration
def test_single_repository_write(repository: MyRepository):
    value = "123"
    my_item = MyModel(field=value, events=[MyEventAdd(field=value)])
    repository.write(my_item)
    assert repository.read(id=value).dict() == my_item.dict()


@pytest.mark.integration
def test_writes_to_same_key_split_over_batches_repository_write(
    repository: MyRepository,
):
    first_value = "123"
    second_value = "abc"
    third_value = "xyz"

    my_item = MyModel(
        field=first_value,
        events=[
            MyEventAdd(field=first_value),
            MyEventAdd(field=second_value),
            MyEventAdd(field=third_value),
            # batch split should occur here since MyEventDelete requires
            # MyEventAdd to have occurred first
            MyEventDelete(field=first_value),
            MyEventDelete(field=second_value),
            MyEventDelete(field=third_value),
        ],
    )
    db_responses = repository.write(my_item)
    batch_count = len(db_responses)

    with pytest.raises(ItemNotFound):
        repository.read(id=first_value)

    with pytest.raises(ItemNotFound):
        repository.read(id=second_value)

    with pytest.raises(ItemNotFound):
        repository.read(id=third_value)

    assert batch_count == 2


@pytest.mark.integration
@pytest.mark.parametrize(
    ["number_of_adds", "number_of_batches"],
    [
        (12, 1),
        (100, 1),
        (101, 2),
        (150, 2),
        (200, 2),
        (201, 3),
    ],
)
def test_writes_to_different_keys_split_over_batches_repository_write(
    repository: MyRepository, number_of_adds: int, number_of_batches: int
):
    my_item = MyModel(
        field="abc",
        events=[MyEventAdd(field=str(i)) for i in range(number_of_adds)],
    )
    db_responses = repository.write(my_item)
    batch_count = len(db_responses)
    assert batch_count == number_of_batches


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
def test_repository_add_and_delete_separate_transactions(repository: MyRepository):
    value = "123"
    my_item = MyModel(field=value, events=[MyEventAdd(field=value)])
    repository.write(my_item)
    intermediate_item = repository.read(id=value)

    assert intermediate_item == my_item

    intermediate_item.events.append(MyEventDelete(field=value))
    repository.write(intermediate_item)

    with pytest.raises(ItemNotFound):
        repository.read(id=value)
