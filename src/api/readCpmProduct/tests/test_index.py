import json
import os
from unittest import mock

import pytest
from domain.core.root.v3 import Root
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from event.json import json_loads
from nhs_context_logging import app_logger

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions

TABLE_NAME = "hiya"
ODS_CODE = "ABC"
PRODUCT_TEAM_ID = "641be376-3954-4339-822c-54071c9ff1a0"
PRODUCT_TEAM_NAME = "product-team-name"
PRODUCT_ID = "P.XXX-YYY"
PRODUCT_NAME = "cpm-product-name"


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(id=PRODUCT_TEAM_ID, name=PRODUCT_TEAM_NAME)

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        cpm_product = product_team.create_cpm_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(cpm_product)

        from api.readCpmProduct.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_id": str(cpm_product.id.id),
                    "product_team_id": str(product_team.id),
                },
            }
        )

    response_body = json_loads(result["body"])

    # Assertions for fields that must exactly match
    assert response_body["id"] == PRODUCT_ID
    assert response_body["product_team_id"] == PRODUCT_TEAM_ID
    assert response_body["name"] == PRODUCT_NAME
    assert response_body["ods_code"] == ODS_CODE
    assert response_body["updated_on"] is None
    assert response_body["deleted_on"] is None

    # Assertions for fields that only need to be included
    assert "product_team_id" in response_body
    assert "created_on" in response_body

    expected_headers = {
        "Content-Type": "application/json",
        "Version": version,
        "Location": None,
    }

    # Check response headers
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Length"] == str(len(result["body"]))
    for key, value in expected_headers.items():
        assert result["headers"][key] == value


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_such_cpm_product(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(id=PRODUCT_TEAM_ID, name=PRODUCT_TEAM_NAME)
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        from api.readCpmProduct.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_id": PRODUCT_ID,
                    "product_team_id": str(product_team.id),
                },
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
                    "diagnostics": f"Could not find object with key '{PRODUCT_ID}'",
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


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_such_product_team(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(id=PRODUCT_TEAM_ID, name=PRODUCT_TEAM_NAME)
    cpm_product = product_team.create_cpm_product(
        name=PRODUCT_NAME, product_id=PRODUCT_ID
    )

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.readCpmProduct.index import handler

        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(cpm_product)

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_id": str(cpm_product.id.id),
                    "product_team_id": str(product_team.id),
                },
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
                    "diagnostics": f"Could not find object with key '{PRODUCT_TEAM_ID}'",
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
