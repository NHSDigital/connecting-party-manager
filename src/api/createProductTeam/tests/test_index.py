import json
import os
from unittest import mock

import pytest
from nhs_context_logging import app_logger

from test_helpers.dynamodb import mock_table
from test_helpers.sample_data import ORGANISATION

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
    assert header_response["Location"] == expected["headers"]["Location"]
    assert result["body"] == expected["body"]
    assert header_response["Content-Length"] == expected["headers"]["Content-Length"]


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    with mock_table(table_name=TABLE_NAME), mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.createProductTeam.index import handler

        result = handler(
            event={"headers": {"version": version}, "body": json.dumps(ORGANISATION)}
        )

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
                                "code": "RESOURCE_CREATED",
                                "display": "Resource created",
                            }
                        ]
                    },
                    "diagnostics": "Resource created",
                }
            ],
        }
    )
    expected = {
        "statusCode": 201,
        "body": expected_body,
        "headers": {
            "Content-Length": str(len(expected_body)),
            "Content-Type": "application/json",
            "Version": version,
            "Location": None,
        },
    }
    _response_assertion(result, expected)


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_bad_payload(version):
    with mock_table(table_name=TABLE_NAME), mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.createProductTeam.index import handler

        result = handler(
            event={"headers": {"version": version}, "body": json.dumps({})}
        )

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
                                "code": "MISSING_VALUE",
                                "display": "Missing value",
                            }
                        ]
                    },
                    "diagnostics": "field required",
                    "expression": ["Organization.resourceType"],
                },
                {
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "MISSING_VALUE",
                                "display": "Missing value",
                            }
                        ]
                    },
                    "diagnostics": "field required",
                    "expression": ["Organization.identifier"],
                },
                {
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "MISSING_VALUE",
                                "display": "Missing value",
                            }
                        ]
                    },
                    "diagnostics": "field required",
                    "expression": ["Organization.name"],
                },
                {
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "MISSING_VALUE",
                                "display": "Missing value",
                            }
                        ]
                    },
                    "diagnostics": "field required",
                    "expression": ["Organization.partOf"],
                },
            ],
        }
    )
    expected = {
        "statusCode": 400,
        "body": expected_body,
        "headers": {
            "Content-Length": str(len(expected_body)),
            "Content-Type": "application/json",
            "Version": version,
            "Location": None,
        },
    }
    _response_assertion(result, expected)
