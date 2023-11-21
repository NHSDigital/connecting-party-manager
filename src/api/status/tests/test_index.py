import json
import os
from unittest import mock

from nhs_context_logging import app_logger


def test_index():
    with mock.patch.dict(os.environ, {"DYNAMODB_TABLE": "hiya"}, clear=True):
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

    assert result == {
        "statusCode": 200,
        "body": expected_body,
        "headers": {
            "Content-Length": len(expected_body),
            "Content-Type": "application/json",
        },
    }
