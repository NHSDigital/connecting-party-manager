import json
import os
from unittest import mock

import pytest
from event.json import json_loads

from test_helpers.dynamodb import mock_table_cpm
from test_helpers.response_assertions import _response_assertions
from test_helpers.sample_data import (
    CPM_PRODUCT_TEAM_NO_ID,
    CPM_PRODUCT_TEAM_NO_ID_DUPED_KEYS,
)

TABLE_NAME = "hiya"


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    with mock_table_cpm(table_name=TABLE_NAME), mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.createProductTeam.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "body": json.dumps(CPM_PRODUCT_TEAM_NO_ID),
            }
        )
    result_body = json_loads(result["body"])
    expected_body = json.dumps(
        {
            "id": result_body["id"],
            "name": "FOOBAR Product Team",
            "ods_code": "F5H1R",
            "status": "active",
            "created_on": result_body["created_on"],
            "updated_on": None,
            "deleted_on": None,
            "keys": [
                {
                    "key_type": "product_team_id",
                    "key_value": "808a36db-a52a-4130-b71e-d9cbcbaed15b",
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
    with mock_table_cpm(table_name=TABLE_NAME), mock.patch.dict(
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
            "errors": [
                {
                    "code": "MISSING_VALUE",
                    "message": "CreateProductTeamIncomingParams.ods_code: field required",
                },
                {
                    "code": "MISSING_VALUE",
                    "message": "CreateProductTeamIncomingParams.name: field required",
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


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_duplicated_keys(version):
    with mock_table_cpm(table_name=TABLE_NAME), mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.createProductTeam.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "body": json.dumps(CPM_PRODUCT_TEAM_NO_ID_DUPED_KEYS),
            }
        )
    expected_body = json.dumps(
        {
            "errors": [
                {
                    "code": "VALIDATION_ERROR",
                    "message": "CreateProductTeamIncomingParams.keys: Ensure that product_team_id only exists once within keys.",
                }
            ]
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
