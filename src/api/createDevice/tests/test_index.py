import json
import os
from unittest import mock

import pytest
from domain.core.root import Root
from domain.repository.product_team_repository.v1 import ProductTeamRepository
from nhs_context_logging import app_logger

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions
from test_helpers.sample_data import DEVICE

TABLE_NAME = "hiya"


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    org = Root.create_ods_organisation(ods_code="ABC")

    # Note 'f9518c12-6c83-4544-97db-d9dd1d64da97' is consistent with DEVICE
    product_team = org.create_product_team(
        id="f9518c12-6c83-4544-97db-d9dd1d64da97", name="product-team-name"
    )

    with mock_table(table_name=TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.createDevice.index import handler

        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        result = handler(
            event={"headers": {"version": version}, "body": json.dumps(DEVICE)}
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
            "Location": "FOO",
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


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
        from api.createDevice.index import handler

        result = handler(
            event={"headers": {"version": version}, "body": json.dumps({})}
        )

    expected_body = json.dumps(
        {
            "errors": [
                {
                    "code": "MISSING_VALUE",
                    "message": "Device.resourceType: field required",
                },
                {
                    "code": "MISSING_VALUE",
                    "message": "Device.deviceName: field required",
                },
                {
                    "code": "MISSING_VALUE",
                    "message": "Device.definition: field required",
                },
                {
                    "code": "MISSING_VALUE",
                    "message": "Device.owner: field required",
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
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )
