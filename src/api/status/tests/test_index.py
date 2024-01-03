import json
import os
from http import HTTPStatus
from unittest import mock

import pytest
from event.status.steps import StatusNotOk, _status_check
from nhs_context_logging import app_logger

from test_helpers.dynamodb import mock_table

TABLE_NAME = "hiya"


def _response_assertion(result, expected):
    assert "statusCode" in result
    assert result["statusCode"] == expected["statusCode"]
    assert "body" in result
    assert "headers" in result
    header_response = result.get("headers", {})
    assert "Content-Type" in header_response
    assert header_response["Content-Type"] == expected["headers"]["Content-Type"]
    assert "Content-Length" in header_response
    assert header_response["Content-Length"] == expected["headers"]["Content-Length"]
    assert "Version" in header_response
    assert header_response["Version"] == expected["headers"]["Version"]
    assert "Location" in header_response
    assert result["body"] == expected["body"]
    assert header_response["Content-Length"] == expected["headers"]["Content-Length"]


def test__status_check():
    with mock_table(table_name=TABLE_NAME) as client:
        result = _status_check(client=client, table_name=TABLE_NAME)
    assert result is HTTPStatus.OK


def test__status_check_not_ok():
    with mock_table(table_name=TABLE_NAME) as client, pytest.raises(StatusNotOk):
        _status_check(client=client, table_name="not a table")


def test_index():
    with mock_table(table_name=TABLE_NAME), mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.status.index import handler

        result = handler(event={})

    expected_body = json.dumps(
        {
            "resourceType": "OperationOutcome",
            "id": app_logger.service_name,
            "meta": {
                "profile": [
                    "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome"
                ]
            },
            "issue": [
                {
                    "severity": "information",
                    "code": "informational",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "OK",
                                "display": "Transaction successful",
                            }
                        ]
                    },
                    "diagnostics": "Transaction successful",
                }
            ],
        }
    )

    expected = {
        "statusCode": 200,
        "body": expected_body,
        "headers": {
            "Content-Length": str(len(expected_body)),
            "Content-Type": "application/json",
            "Version": "null",
            "Location": None,
        },
    }
    _response_assertion(result, expected)


def test_index_not_ok():
    with mock_table(table_name="not-a-table"), mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.status.index import handler

        result = handler(event={})

    expected_body = json.dumps(
        {
            "resourceType": "OperationOutcome",
            "id": app_logger.service_name,
            "meta": {
                "profile": [
                    "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome"
                ]
            },
            "issue": [
                {
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "SERVICE_UNAVAILABLE",
                                "display": "Service unavailable - could be temporary",
                            }
                        ]
                    },
                    "diagnostics": "An error occurred (ResourceNotFoundException) when calling the Scan operation: Requested resource not found",
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
    _response_assertion(result, expected)
