import json
import os
from unittest import mock

import pytest
from nhs_context_logging import app_logger

from .data import organisation


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    with mock.patch.dict(os.environ, {"DYNAMODB_TABLE": "hiya"}, clear=True):
        from api.createProductTeam.index import handler

        result = handler(
            event={"headers": {"version": version}, "body": json.dumps(organisation)}
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
    assert result == {
        "statusCode": 201,
        "body": expected_body,
        "headers": {
            "Content-Length": len(expected_body),
            "Content-Type": "application/json",
        },
    }
