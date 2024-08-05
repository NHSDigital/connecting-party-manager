import json
import os
from unittest import mock

import pytest
from domain.repository.device_repository.mock_search_responses.mock_responses import (
    device_5NR_result,
)

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions

TABLE_NAME = "hiya"


@pytest.mark.parametrize(
    "params, expected_body",
    [
        (
            {
                "nhs_as_client": "5NR",
                "nhs_as_svc_ia": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment",
            },
            device_5NR_result,
        ),
        (
            {
                "nhs_as_client": "5NR",
                "nhs_as_svc_ia": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment",
                "nhs_mhs_manufacturer_org": "LSP02",
            },
            device_5NR_result,
        ),
    ],
)
def test_index(params, expected_body):
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchSdsDevice.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client
        result = handler(
            event={
                "headers": {"version": 1},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )
    expected = {
        "statusCode": 200,
        "body": json.dumps(expected_body),
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(json.dumps(expected_body))),
            "Version": "1",
            "Location": None,
            "Host": "foo.co.uk",
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.parametrize(
    "params, error, statusCode",
    [
        ({"nhs_as_client": "5NR"}, "MISSING_VALUE", 400),
        (
            {
                "nhs_as_svc_ia": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment",
                "nhs_mhs_manufacturer_org": "LSP02",
            },
            "MISSING_VALUE",
            400,
        ),
        ({"nhs_mhs_manufacturer_org": "LSP02"}, "MISSING_VALUE", 400),
        (
            {
                "nhs_as_client": "5NR",
                "nhs_as_svc_ia": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment",
                "foo": "bar",
            },
            "VALIDATION_ERROR",
            400,
        ),
    ],
)
def test_filter_errors(params, error, statusCode):
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchSdsDevice.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client
        result = handler(
            event={
                "headers": {"version": 1},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )
    assert result["statusCode"] == statusCode
    assert error in result["body"]
