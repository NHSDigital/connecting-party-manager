import json
import os
from contextlib import contextmanager
from datetime import datetime
from types import ModuleType
from typing import Any, Generator
from unittest import mock

import pytest
from domain.core.cpm_product import CpmProduct
from domain.core.cpm_system_id import ProductId
from domain.core.device import Device
from domain.core.product_key import ProductKeyType
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.device_repository import DeviceRepository
from domain.repository.product_team_repository import ProductTeamRepository
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"
DEVICE_NAME = "Product-MHS"
ODS_CODE = "AAA"
PRODUCT_ID = ProductId.create()
PRODUCT_TEAM_NAME = "My Product Team"
PRODUCT_NAME = "My Product"
VERSION = 1

QUESTIONNAIRE_DATA = {
    "Address": "http://example.com",
    "Unique Identifier": "123456",
    "Managing Organization": "Example Org",
    "MHS Party key": "party-key-001",
    "MHS CPA ID": "cpa-id-001",
    "Approver URP": "approver-123",
    "Contract Property Template Key": "contract-key-001",
    "Date Approved": "2024-01-01",
    "Date DNS Approved": "2024-01-02",
    "Date Requested": "2024-01-03",
    "DNS Approver": "dns-approver-456",
    "Interaction Type": "FHIR",
    "MHS FQDN": "mhs.example.com",
    "MHS Is Authenticated": "PERSISTENT",
    "Product Key": "product-key-001",
    "Requestor URP": "requestor-789",
}


@contextmanager
def mock_epr_product() -> Generator[tuple[ModuleType, CpmProduct], Any, None]:
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(name=PRODUCT_TEAM_NAME)

    with mock_table(table_name=TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {"DYNAMODB_TABLE": TABLE_NAME, "AWS_DEFAULT_REGION": "eu-west-2"},
        clear=True,
    ):
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        product = product_team.create_cpm_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value="ABC1234-987654")
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(entity=product)

        import api.createDeviceMessageHandlingSystem.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product


@contextmanager
def mock_not_epr_product() -> Generator[tuple[ModuleType, CpmProduct], Any, None]:
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(name=PRODUCT_TEAM_NAME)

    with mock_table(table_name=TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {"DYNAMODB_TABLE": TABLE_NAME, "AWS_DEFAULT_REGION": "eu-west-2"},
        clear=True,
    ):
        product_team_repo = ProductTeamRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_team_repo.write(entity=product_team)

        product = product_team.create_cpm_product(
            name=PRODUCT_NAME, product_id=PRODUCT_ID
        )
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(entity=product)

        import api.createDeviceMessageHandlingSystem.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product


def test_index() -> None:
    with mock_epr_product() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {"questionnaire_responses": {"spine_mhs": [QUESTIONNAIRE_DATA]}}
                ),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
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
        assert device.created_on.date() == datetime.today().date()
        assert device.updated_on.date() == datetime.today().date()
        assert not device.deleted_on

        questionnaire_responses = device.questionnaire_responses["spine_mhs/1"]
        assert len(questionnaire_responses) == 1
        questionnaire_response = questionnaire_responses[0]
        assert questionnaire_response.data == QUESTIONNAIRE_DATA

        # Retrieve the created resource
        repo = DeviceRepository(
            table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
        )
        created_device = repo.read(
            product_team_id=device.product_team_id,
            product_id=device.product_id,
            id=device.id,
        )

        # Check party_key is added to tags in the created device
        expected_party_key = (str(ProductKeyType.PARTY_KEY), "abc1234-987654")
        assert any(expected_party_key in tag.__root__ for tag in created_device.tags)


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
            {"questionnaire_responses": {"spine_mhs": [QUESTIONNAIRE_DATA]}},
            {},
            "MISSING_VALUE",
            400,
        ),
        (
            {
                "questionnaire_responses": {"spine_mhs": [QUESTIONNAIRE_DATA]},
                "forbidden_extra_param": "foo",
            },
            {"product_id": str(PRODUCT_ID), "product_team_id": consistent_uuid(1)},
            "VALIDATION_ERROR",
            400,
        ),
        (
            {"questionnaire_responses": {"spine_mhs": [QUESTIONNAIRE_DATA]}},
            {
                "product_id": str(PRODUCT_ID),
                "product_team_id": "id_that_does_not_exist",
            },
            "RESOURCE_NOT_FOUND",
            404,
        ),
    ],
)
def test_incoming_errors(body, path_parameters, error_code, status_code):
    with mock_epr_product() as (index, _):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(body),
                "pathParameters": path_parameters,
            }
        )

        # Validate that the response indicates that the expected error occured
        assert response["statusCode"] == status_code
        assert error_code in response["body"]


@pytest.mark.parametrize(
    ["body", "error_code", "error_message", "status_code"],
    [
        (
            {
                "questionnaire_responses": {
                    "spine_mhs": [QUESTIONNAIRE_DATA, QUESTIONNAIRE_DATA]
                },
            },
            "VALIDATION_ERROR",
            "Expected only one response for the 'spine_mhs' questionnaire",
            400,
        ),
        (
            {
                "questionnaire_responses": {
                    "spine_mhs": [{"Address": "http://example.com"}]
                }
            },
            "MISSING_VALUE",
            "Failed to validate data against 'spine_mhs/1': 'Unique Identifier' is a required property",
            400,
        ),
    ],
)
def test_questionnaire_response_validation_errors(
    body, error_code, error_message, status_code
):
    with mock_epr_product() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(body),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                },
            }
        )

        # Validate that the response indicates that the expected error occured
        assert response["statusCode"] == status_code
        assert error_code in response["body"]
        assert error_message in response["body"]


def test_not_epr_product():
    with mock_not_epr_product() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {"questionnaire_responses": {"spine_mhs": [QUESTIONNAIRE_DATA]}}
                ),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                },
            }
        )

        assert response["statusCode"] == 400
        expected_error_code = "VALIDATION_ERROR"
        expected_message_code = "Not an EPR Product: Cannot create MHS device for product without exactly one Party Key"
        assert expected_error_code in response["body"]
        assert expected_message_code in response["body"]
