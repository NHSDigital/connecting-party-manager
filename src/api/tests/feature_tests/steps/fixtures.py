import os
from unittest import mock

from behave import fixture

from api.tests.feature_tests.steps.context import Context
from api.tests.feature_tests.steps.endpoint_lambda_mapping import (
    get_endpoint_lambda_mapping,
)
from api.tests.feature_tests.steps.requests import mock_request
from test_helpers.dynamodb import mock_table


@fixture(name="fixture.mock.dynamodb")
def mock_dynamodb(context: Context, table_name):
    with mock_table(table_name=table_name) as dynamodb_client:
        endpoint_lambda_mapping = get_endpoint_lambda_mapping()
        for path_index_mapping in endpoint_lambda_mapping.values():
            for index in path_index_mapping.values():
                index.cache["DYNAMODB_CLIENT"] = dynamodb_client
        yield


@fixture(name="fixture.mock.requests")
def mock_requests(context, *args, **kwargs):
    """Wrap up the above context manager as a behave fixture"""
    with mock_request():
        yield


@fixture(name="fixture.mock.environment")
def mock_environment(context, table_name):
    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        yield
