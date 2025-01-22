import json
import os
from unittest import mock

import pytest
from domain.core.root import Root
from domain.repository.product_team_repository import ProductTeamRepository
from event.json import json_loads

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
    product_team = org.create_product_team_epr(
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
        from api.readProductTeam.index import cache, handler

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
    result_body = json_loads(result["body"])
    expected_result = json.dumps(
        {
            "id": result_body["id"],
            "name": "FOOBAR Product Team",
            "ods_code": "F5H1R",
            "status": "active",
            "created_on": result_body["created_on"],
            "updated_on": None,
            "deleted_on": None,
            "keys": [{"key_type": "product_team_id_alias", "key_value": "BAR"}],
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
    [("1", "123"), ("1", f"F5H1R.{consistent_uuid(1)}")],
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
        from api.readProductTeam.index import cache, handler

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
    product_team = org.create_product_team_epr(
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
        from api.readProductTeam.index import cache, handler

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
    result_body = json_loads(result["body"])
    expected_result = json.dumps(
        {
            "id": result_body["id"],
            "name": "FOOBAR Product Team",
            "ods_code": "F5H1R",
            "status": "active",
            "created_on": result_body["created_on"],
            "updated_on": None,
            "deleted_on": None,
            "keys": [{"key_type": "product_team_id_alias", "key_value": "BAR"}],
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
