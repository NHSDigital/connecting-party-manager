import os
from unittest import mock

from behave import fixture

from feature_tests.end_to_end.steps.requests import mock_request
from test_helpers.dynamodb import mock_table


@fixture(name="fixture.mock.dynamodb")
def mock_dynamodb(context, table_name):
    with mock_table(table_name=table_name):
        yield


@fixture(name="fixture.mock.requests")
def mock_requests(context, *args, **kwargs):
    """Wrap up the above context manager as a behave fixture"""
    with mock_request():
        yield


@fixture(name="fixture.mock.environment")
def mock_environment(context, table_name):
    with mock.patch.dict(os.environ, {"DYNAMODB_TABLE": table_name}, clear=True):
        yield
