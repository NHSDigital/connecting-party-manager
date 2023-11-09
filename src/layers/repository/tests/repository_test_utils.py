import pytest
from pynamodb.attributes import UnicodeAttribute
from repository.errors import ItemNotFound
from repository.model import BaseModel
from repository.repository import Repository


class MyTestModel(BaseModel, discriminator="MyTestModel"):
    id = UnicodeAttribute()
    name = UnicodeAttribute()


def _test_read_my_test_model_mock_not_exists(create_table=False):
    if create_table:
        MyTestModel.create_table(wait=True)

    repository = Repository[MyTestModel](model=MyTestModel)
    non_existent_pk = "non_existent_pk"
    with pytest.raises(ItemNotFound):
        repository.read(pk=non_existent_pk)


def _test_read_write_my_test_model_mock(create_table=False):
    if create_table:
        MyTestModel.create_table(wait=True)

    repository = Repository[MyTestModel](model=MyTestModel)
    record_data = {
        "id": "record_id",
        "name": "Record Name",
        "pk_1": "foo",
        "sk_1": "bar",
        "pk_2": "foo",
        "sk_2": "bar",
    }

    repository.create(record_data)
    # Verify that the record exists by reading it
    created_record = repository.read(pk="MyTestModel#record_id")
    # Assert that the read record matches the expected data
    assert created_record.id == "record_id"
    assert created_record.name == "Record Name"
