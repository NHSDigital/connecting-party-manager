import json
import os
from contextlib import contextmanager
from datetime import datetime
from types import ModuleType
from typing import Any, Generator
from unittest import mock

import pytest
from domain.core.cpm_system_id import ProductId
from domain.core.device import Device
from domain.core.enum import Environment
from domain.core.epr_product import EprProduct
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"

DEVICE_NAME = "My Device"
ODS_CODE = "AAA"
PRODUCT_ID = ProductId.create()
PRODUCT_TEAM_NAME = "My Product Team"
PRODUCT_NAME = "My Product"
VERSION = 1


@contextmanager
def mock_product() -> Generator[tuple[ModuleType, EprProduct], Any, None]:
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team_epr(name=PRODUCT_TEAM_NAME)

    with mock_table(table_name=TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {"DYNAMODB_TABLE": TABLE_NAME, "AWS_DEFAULT_REGION": "eu-west-2"},
        clear=True,
    ):
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        product = product_team.create_epr_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product_repo = EprProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(entity=product)

        import api.createDevice.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product


def test_index() -> None:
    with mock_product() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps({"name": DEVICE_NAME}),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                    "environment": "dev",
                },
            }
        )

        # Validate that the response indicates that a resource was created
        assert response["statusCode"] == 201
        _device = json_loads(response["body"])
        device = Device(**_device)
        assert device.product_team_id == product.product_team_id
        assert device.product_id == product.id
        assert device.name == DEVICE_NAME
        assert device.ods_code == ODS_CODE
        assert device.environment == Environment.DEV
        assert device.created_on.date() == datetime.today().date()
        assert not device.updated_on
        assert not device.deleted_on
        # Retrieve the created resource
        repo = DeviceRepository(
            table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
        )
        created_device = repo.read(
            product_team_id=device.product_team_id,
            product_id=device.product_id,
            environment=Environment.DEV,
            id=device.id,
        )
        assert created_device == device


@pytest.mark.parametrize(
    ["body", "path_parameters", "error_code", "status_code"],
    [
        (
            {},
            {"product_team_id": consistent_uuid(1)},
            "MISSING_VALUE",
            400,
        ),
        (
            {"name": DEVICE_NAME},
            {},
            "MISSING_VALUE",
            400,
        ),
        (
            {"name": DEVICE_NAME, "forbidden_extra_param": "foo"},
            {
                "product_id": str(PRODUCT_ID),
                "product_team_id": consistent_uuid(1),
                "environment": "dev",
            },
            "VALIDATION_ERROR",
            400,
        ),
        (
            {"name": DEVICE_NAME},
            {
                "product_id": str(PRODUCT_ID),
                "product_team_id": "id_that_does_not_exist",
                "environment": "dev",
            },
            "RESOURCE_NOT_FOUND",
            404,
        ),
        (
            {"name": DEVICE_NAME},
            {
                "product_id": str(PRODUCT_ID),
                "product_team_id": consistent_uuid(1),
                "environment": "FOO",
            },
            "VALIDATION_ERROR",
            400,
        ),
    ],
)
def test_incoming_errors(body, path_parameters, error_code, status_code):
    with mock_product() as (index, _):
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
