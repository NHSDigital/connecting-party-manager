import json
import os
from http import HTTPStatus
from unittest import mock

import pytest
from event.status.steps import StatusNotOk, _status_check

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions

TABLE_NAME = "hiya"


def test__status_check():
    with mock_table(table_name=TABLE_NAME) as client:
        result = _status_check(client=client, table_name=TABLE_NAME)
    assert result == HTTPStatus.OK


def test__status_check_not_ok():
    with mock_table(table_name=TABLE_NAME) as client, pytest.raises(StatusNotOk):
        _status_check(client=client, table_name="not a table")


def test_index():
    with mock_table(table_name=TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.status.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client

        result = handler(event={})

    expected = {
        "statusCode": 200,
        "body": "200",
        "headers": {
            "Content-Length": str(len("200")),
            "Content-Type": "application/json",
            "Version": "null",
            "Location": None,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


def test_index_not_ok():
    with mock_table(table_name="not-a-table") as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.status.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client

        result = handler(event={})

    expected_body = json.dumps(
        {
            "errors": [
                {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "An error occurred (ResourceNotFoundException) when calling the Scan operation: Requested resource not found",
                }
            ],
        }
    )

    expected = {
        "statusCode": 503,
        "body": expected_body,
        "headers": {
            "Content-Length": str(len(expected_body)),
            "Content-Type": "application/json",
            "Version": "null",
            "Location": None,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )
