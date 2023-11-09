import os
from unittest import mock

from moto import mock_dynamodb


@mock_dynamodb
def test_read_my_test_model_mock_not_exists():
    with mock.patch.dict(os.environ, {"DYNAMODB_TABLE": "test-table"}):
        from .repository_test_utils import _test_read_my_test_model_mock_not_exists

        _test_read_my_test_model_mock_not_exists(create_table=True)


@mock_dynamodb
def test_read_write_my_test_model_mock():
    with mock.patch.dict(os.environ, {"DYNAMODB_TABLE": "test-table"}):
        from .repository_test_utils import _test_read_write_my_test_model_mock

        _test_read_write_my_test_model_mock(create_table=True)
