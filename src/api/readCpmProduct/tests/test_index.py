import json
import os
from unittest import mock

import pytest
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.product_team_repository import ProductTeamRepository
from event.json import json_loads

from test_helpers.dynamodb import mock_table_cpm
from test_helpers.response_assertions import _response_assertions

TABLE_NAME = "hiya"
ODS_CODE = "F5H1R"
PRODUCT_TEAM_ID = "641be376-3954-4339-822c-54071c9ff1a0"
PRODUCT_TEAM_NAME = "product-team-name"
PRODUCT_ID = "P.XXX-YYY"
PRODUCT_NAME = "cpm-product-name"
PRODUCT_TEAM_KEYS = [
    {"key_type": "product_team_id", "key_value": "808a36db-a52a-4130-b71e-d9cbcbaed15b"}
]


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )

    with mock_table_cpm(TABLE_NAME) as client, mock.patch.dict(
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
                },
            }
        )
    response_body = json_loads(result["body"])

    # Assertions for fields that must exactly match
    assert response_body["id"] == PRODUCT_ID
    assert response_body["cpm_product_team_id"] == product_team.id
    assert response_body["name"] == PRODUCT_NAME
    assert response_body["ods_code"] == ODS_CODE
    assert response_body["updated_on"] is None
    assert response_body["deleted_on"] is None

    # Assertions for fields that only need to be included
    assert "cpm_product_team_id" in response_body
    assert "created_on" in response_body

    expected_headers = {
        "Content-Type": "application/json",
        "Version": version,
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
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    with mock_table_cpm(TABLE_NAME) as client, mock.patch.dict(
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
                },
            }
        )

    expected_result = json.dumps(
        {
            "errors": [
                {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"Could not find CpmProduct for key ('{PRODUCT_ID}')",
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
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )
