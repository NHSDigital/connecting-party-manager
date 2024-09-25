import json
import os
from unittest import mock

import pytest
from domain.core.root import Root
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from nhs_context_logging import app_logger

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions

from .data import product_payload, product_team_payload

TABLE_NAME = "hiya"


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    org = Root.create_ods_organisation(ods_code=product_team_payload["ods_code"])

    product_team = org.create_product_team(
        id=product_team_payload["id"], name=product_team_payload["name"]
    )

    with mock_table(table_name=TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.createCpmProduct.index import handler

        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        result = handler(
            event={
                "headers": {"version": version},
                "body": json.dumps(product_payload),
                "pathParameters": {"product_team_id": product_team_payload["id"]},
            }
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
    "params, error, status_code, version",
    [
        ({}, "MISSING_VALUE", 400, "1"),
        (
            {
                "product_name": "Foobar product",
                "foo": "bar",
            },
            "VALIDATION_ERROR",
            400,
            "1",
        ),
    ],
)
def test_incoming_errors(params, error, status_code, version):
    org = Root.create_ods_organisation(ods_code=product_team_payload["ods_code"])

    product_team = org.create_product_team(
        id=product_team_payload["id"], name=product_team_payload["name"]
    )

    with mock_table(table_name=TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.createCpmProduct.index import handler

        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        result = handler(
            event={
                "headers": {"version": version},
                "body": json.dumps(params),
                "pathParameters": {"product_team_id": product_team_payload["id"]},
            }
        )
    assert result["statusCode"] == status_code
    assert error in result["body"]


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_such_product_team(version):
    with mock_table(TABLE_NAME), mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.createCpmProduct.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "body": json.dumps(product_payload),
                "pathParameters": {"product_team_id": "FOOBAR"},
            }
        )
    expected_result = json.dumps(
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
                                "code": "RESOURCE_NOT_FOUND",
                                "display": "Resource not found",
                            }
                        ]
                    },
                    "diagnostics": "Could not find object with key 'FOOBAR'",
                }
            ],
        }
    )

    expected = {
        "statusCode": 404,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
            "Location": None,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )
