import json
import os
from unittest import mock

import pytest
from domain.core.enum import Environment
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.product_team_repository import ProductTeamRepository
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions

TABLE_NAME = "hiya"
ODS_CODE = "F5H1R"
PRODUCT_TEAM_ID = "F5H1R.641be376-3954-4339-822c-54071c9ff1a0"
PRODUCT_TEAM_NAME = "product-team-name"
PRODUCT_ID = "P.XXX-YYY"
PRODUCT_NAME = "cpm-product-name"
PRODUCT_TEAM_KEYS = [{"key_type": "product_team_id_alias", "key_value": "BAR"}]
DEVICE_REFERENCE_DATA_NAME = "device-reference-data"


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

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        # Set up Product in DB
        cpm_product = product_team.create_cpm_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(cpm_product)

        # Set up DeviceReferenceData in DB
        device_reference_data = cpm_product.create_device_reference_data(
            name=DEVICE_REFERENCE_DATA_NAME, environment=Environment.DEV
        )
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data)

        from api.readDeviceReferenceData.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(cpm_product.id.id),
                    "environment": Environment.DEV,
                    "device_reference_data_id": str(device_reference_data.id),
                },
            }
        )

    response_body = json_loads(result["body"])

    # Assertions for fields that must exactly match
    assert response_body["id"] == str(device_reference_data.id)
    assert response_body["product_id"] == str(cpm_product.id)
    assert response_body["product_team_id"] == str(product_team.id)
    assert response_body["name"] == device_reference_data.name
    assert response_body["environment"] == Environment.DEV
    assert response_body["ods_code"] == device_reference_data.ods_code
    assert response_body["updated_on"] is None
    assert response_body["deleted_on"] is None

    # Assertions for fields that only need to be included
    assert "product_team_id" in response_body
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
def test_index_no_such_device_reference_data(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        # Set up Product in DB
        cpm_product = product_team.create_cpm_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(cpm_product)

        from api.readDeviceReferenceData.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(cpm_product.id),
                    "environment": Environment.DEV,
                    "device_reference_data_id": "does not exist",
                },
            }
        )

    expected_result = json.dumps(
        {
            "errors": [
                {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"Could not find DeviceReferenceData for key ('{product_team.id}', '{cpm_product.id}', 'DEV', 'does not exist')",
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
def test_index_no_such_product(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        from api.readDeviceReferenceData.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": "product that doesnt exist",
                    "environment": Environment.DEV,
                    "device_reference_data_id": "does not exist",
                },
            }
        )

    expected_result = json.dumps(
        {
            "errors": [
                {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"Could not find CpmProduct for key ('{product_team.id}', 'product that doesnt exist')",
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
def test_index_no_such_product_team(version):
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.readDeviceReferenceData.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_id": str(PRODUCT_ID),
                    "product_team_id": str(PRODUCT_TEAM_ID),
                    "environment": Environment.DEV,
                    "device_reference_data_id": "123",
                },
            }
        )

    expected_result = json.dumps(
        {
            "errors": [
                {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": f"Could not find ProductTeam for key ('{PRODUCT_TEAM_ID}')",
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
def test_index_incorrect_env(version):
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(
        name=PRODUCT_TEAM_NAME, keys=PRODUCT_TEAM_KEYS
    )

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        # Set up ProductTeam in DB
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        # Set up Product in DB
        cpm_product = product_team.create_cpm_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(cpm_product)

        # Set up DeviceReferenceData in DB
        device_reference_data = cpm_product.create_device_reference_data(
            name=DEVICE_REFERENCE_DATA_NAME, environment=Environment.DEV
        )
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data)
        # Set up Device in DB

        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(cpm_product.id.id),
                    "environment": "prod",
                    "device_id": str(device_reference_data.id),
                },
            }
        )

        expected_result = json.dumps(
            {
                "errors": [
                    {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": f"Could not find Device for key ('{product_team.id}', '{cpm_product.id.id}', 'PROD', '{device_reference_data.id}')",
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
