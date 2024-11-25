import pytest
from domain.repository.errors import AlreadyExistsError, ItemNotFound
from domain.repository.repository import (
    exponential_backoff_with_jitter,
    retry_with_jitter,
)

from .model_v1 import (
    MyEventAdd,
    MyEventDelete,
    MyModel,
    MyOtherEventAdd,
    MyRepository,
    MyTableKey,
)


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


@pytest.mark.integration
def test_repository_write_bulk(repository: MyRepository):
    responses = repository.write_bulk(
        [
            {
                "pk": str(i),
                "sk": str(i),
                "pk_read": MyTableKey.FOO.key(str(i)),
                "sk_read": MyTableKey.FOO.key(str(i)),
                "field": f"boo-{i}",
            }
            for i in range(51)
        ],
        batch_size=25,
    )
    assert len(responses) >= 3  # 51/25

    for i in range(51):
        assert repository.read(id=str(i)).field == f"boo-{i}"


def test_exponential_backoff_with_jitter():
    base_delay = 0.1
    max_delay = 5
    min_delay = 0.05
    n_samples = 1000

    delays = []
    for retry in range(n_samples):
        delay = exponential_backoff_with_jitter(
            n_retries=retry,
            base_delay=base_delay,
            min_delay=min_delay,
            max_delay=max_delay,
        )
        assert max_delay >= delay >= min_delay
        delays.append(delay)
    assert len(set(delays)) == n_samples  # all delays should be unique
    assert sum(delays[n_samples:]) < sum(
        delays[:n_samples]
    )  # final delays should be larger than first delays


@pytest.mark.parametrize(
    "error_code",
    [
        "ProvisionedThroughputExceededException",
        "ThrottlingException",
        "InternalServerError",
    ],
)
def test_retry_with_jitter_all_fail(error_code: str):
    class MockException(Exception):
        def __init__(self, error_code):
            self.response = {"Error": {"Code": error_code}}

    max_retries = 3

    @retry_with_jitter(max_retries=max_retries, error=MockException)
    def throw(error_code):
        raise MockException(error_code=error_code)

    with pytest.raises(ExceptionGroup) as exception_info:
        throw(error_code=error_code)

    assert (
        exception_info.value.message
        == f"Failed to put item after {max_retries} retries"
    )
    assert len(exception_info.value.exceptions) == max_retries
    assert all(
        isinstance(exc, MockException) for exc in exception_info.value.exceptions
    )


@pytest.mark.parametrize(
    "error_code",
    [
        "ProvisionedThroughputExceededException",
        "ThrottlingException",
        "InternalServerError",
    ],
)
def test_retry_with_jitter_third_passes(error_code: str):
    class MockException(Exception):
        retries = 0

        def __init__(self, error_code):
            self.response = {"Error": {"Code": error_code}}

    max_retries = 3

    @retry_with_jitter(max_retries=max_retries, error=MockException)
    def throw(error_code):
        if MockException.retries == max_retries - 1:
            return "foo"
        MockException.retries += 1
        raise MockException(error_code=error_code)

    assert throw(error_code=error_code) == "foo"


@pytest.mark.parametrize(
    "error_code",
    [
        "SomeOtherError",
    ],
)
def test_retry_with_jitter_other_code(error_code: str):
    class MockException(Exception):
        def __init__(self, error_code):
            self.response = {"Error": {"Code": error_code}}

    @retry_with_jitter(max_retries=3, error=MockException)
    def throw(error_code):
        raise MockException(error_code=error_code)

    with pytest.raises(MockException) as exception_info:
        throw(error_code=error_code)

    assert exception_info.value.response == {"Error": {"Code": error_code}}


def test_retry_with_jitter_other_exception():
    @retry_with_jitter(max_retries=3, error=ValueError)
    def throw():
        raise TypeError()

    with pytest.raises(TypeError):
        throw()
