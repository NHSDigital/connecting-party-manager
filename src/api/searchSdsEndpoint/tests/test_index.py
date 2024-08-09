import json
import os
from unittest import mock

import pytest
from domain.repository.device_repository.mock_search_responses.mock_responses import (
    endpoint_RTX_result,
)

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions

TABLE_NAME = "hiya"


@pytest.mark.parametrize(
    "params, expected_body",
    [
        (
            {
                "nhs_id_code": "RTX",
                "nhs_mhs_svc_ia": "urn:nhs:names:services:ebs:PRSC_IN040000UK08",
            },
            endpoint_RTX_result,
        ),
        (
            {"nhs_id_code": "RTX", "nhs_mhs_party_key": "D81631-827817"},
            endpoint_RTX_result,
        ),
        (
            {
                "nhs_mhs_svc_ia": "urn:nhs:names:services:ebs:PRSC_IN040000UK08",
                "nhs_mhs_party_key": "D81631-827817",
            },
            endpoint_RTX_result,
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
        from api.searchSdsEndpoint.index import cache, handler

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
        (
            {
                "nhs_id_code": "RTX",
            },
            "VALIDATION_ERROR",
            400,
        ),
        (
            {"nhs_mhs_svc_ia": "urn:nhs:names:services:ebs:PRSC_IN040000UK08"},
            "VALIDATION_ERROR",
            400,
        ),
        ({"nhs_mhs_party_key": "D81631-827817"}, "VALIDATION_ERROR", 400),
        (
            {
                "nhs_id_code": "RTX",
                "nhs_mhs_svc_ia": "urn:nhs:names:services:ebs:PRSC_IN040000UK08",
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
        from api.searchSdsEndpoint.index import cache, handler

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
