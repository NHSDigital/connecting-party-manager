import json
import os
from contextlib import contextmanager
from datetime import datetime
from unittest import mock

import pytest
from domain.core.cpm_system_id.v1 import PartyKeyId, ProductId
from domain.core.enum import Status
from domain.core.root.v3 import Root
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from event.json import json_loads
from nhs_context_logging import app_logger

from test_helpers.dynamodb import mock_table
from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"
ODS_CODE = "F5H1R"
PRODUCT_TEAM_ID = consistent_uuid(1)
PRODUCT_NAME = "My Product"
PRODUCT_TEAM_KEYS = CPM_PRODUCT_TEAM_NO_ID["keys"]
VERSION = 1
RESOURCE_CREATED = {
    "resourceType": "OperationOutcome",
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


@contextmanager
def mock_lambda():
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    product_team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )

    with mock_table(table_name=TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {"DYNAMODB_TABLE": TABLE_NAME, "AWS_DEFAULT_REGION": "eu-west-2"},
        clear=True,
    ):
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        import api.createCpmProductForEpr.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product_team


def test_index():
    with mock_lambda() as (index, product_team):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps({"product_name": PRODUCT_NAME}),
                "pathParameters": {"product_team_id": product_team.id},
            }
        )
        # Validate that the response indicates that a resource was created
        assert response["statusCode"] == 201
        assert json_loads(response["body"]) == {
            "id": app_logger.service_name,
            **RESOURCE_CREATED,
        }

        # Retrieve the created resource
        repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
        )
        created_product = repo.read(
            product_team_id=product_team.id, product_id=response["headers"]["Location"]
        ).dict()

    # Sense checks on the created resource
    assert isinstance(created_product.pop("created_on"), datetime)
    assert isinstance(created_product.pop("updated_on"), datetime)
    assert ProductId.validate_cpm_system_id(created_product.pop("id"))
    assert PartyKeyId.validate_cpm_system_id(
        created_product.pop("keys")[0]["key_value"]
    )
    assert created_product == {
        "deleted_on": None,
        "name": PRODUCT_NAME,
        "ods_code": ODS_CODE,
        "product_team_id": product_team.id,
        "status": Status.ACTIVE,
    }


@pytest.mark.parametrize(
    ["body", "path_parameters", "error_code", "status_code"],
    [
        (
            {},
            {"product_team_id": PRODUCT_TEAM_ID},
            "MISSING_VALUE",
            400,
        ),
        (
            {"product_name": PRODUCT_NAME},
            {},
            "MISSING_VALUE",
            400,
        ),
        (
            {"product_name": PRODUCT_NAME, "forbidden_extra_param": "foo"},
            {"product_team_id": PRODUCT_TEAM_ID},
            "VALIDATION_ERROR",
            400,
        ),
        (
            {"product_name": PRODUCT_NAME},
            {"product_team_id": "id_that_does_not_exist"},
            "RESOURCE_NOT_FOUND",
            404,
        ),
    ],
)
def test_incoming_errors(body, path_parameters, error_code, status_code):
    with mock_lambda() as (index, product_team):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(body),
                "pathParameters": path_parameters,
            }
        )

        # Validate that the response indicates that the expected error
        assert response["statusCode"] == status_code
        assert error_code in response["body"]
