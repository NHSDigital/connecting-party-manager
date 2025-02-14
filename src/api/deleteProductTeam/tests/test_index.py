import json
import os
from unittest import mock

import pytest
from domain.core.root import Root
from domain.repository.cpm_product_repository.v1 import CpmProductRepository
from domain.repository.product_team_repository import ProductTeamRepository

from test_helpers.dynamodb import mock_table_cpm
from test_helpers.response_assertions import _response_assertions
from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    product_team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )

    with mock_table_cpm(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.deleteProductTeam.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client

        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {"product_team_id": product_team.id},
            }
        )
    expected_result = json.dumps(
        {
            "code": "RESOURCE_DELETED",
            "message": f"{product_team.id} has been deleted.",
        }
    )

    expected = {
        "statusCode": 200,
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


@pytest.mark.parametrize(
    "version, product_id",
    [("1", "123"), ("1", f"{consistent_uuid(1)}")],
)
def test_index_no_such_product_team(version, product_id):
    with mock_table_cpm(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.deleteProductTeam.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {"product_team_id": product_id},
            }
        )

    expected_result = json.dumps(
        {
            "errors": [
                {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"Could not find ProductTeam for key ('{product_id}')",
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


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_by_alias(version):
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    product_team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )

    with mock_table_cpm(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.deleteProductTeam.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client

        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {"product_team_id": "BAR"},
            }
        )
    expected_result = json.dumps(
        {
            "code": "RESOURCE_DELETED",
            "message": f"{product_team.id} has been deleted.",
        }
    )

    expected = {
        "statusCode": 200,
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


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_existing_products(version):
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    product_team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )
    product = product_team.create_cpm_product(name="Foo")

    with mock_table_cpm(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.deleteProductTeam.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client

        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(entity=product)

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {"product_team_id": product_team.id},
            }
        )
    expected_result = json.dumps(
        {
            "errors": [
                {
                    "code": "CONFLICT",
                    "message": f"Product Team cannot be deleted as it still has associated Product Ids ['{product.id}']",
                }
            ]
        }
    )

    expected = {
        "statusCode": 409,
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
