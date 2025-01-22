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
from domain.core.enum import Environment
from domain.core.product_key import ProductKeyType
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository import DeviceRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from event.json import json_loads
from sds.epr.constants import EprNameTemplate
from sds.epr.utils import is_mhs_device

from test_helpers.dynamodb import mock_table
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"
DEVICE_NAME = "ABC1234-987654 - Message Handling System"
ODS_CODE = "AAA"
PRODUCT_ID = ProductId.create()
PRODUCT_TEAM_NAME = "My Product Team"
PRODUCT_NAME = "My Product"
VERSION = 1
PARTY_KEY = "ABC1234-987654"

QUESTIONNAIRE_DATA = {
    "MHS FQDN": "mhs.example.com",
    "MHS Service Description": "Example Description",
    "MHS Manufacturer Organisation": "F5H1R",
    "Product Name": "Product Name",
    "Product Version": "1",
    "Approver URP": "UI provided",
    "DNS Approver": "UI provided",
    "Requestor URP": "UI provided",
}
QUESTIONNAIRE_DATA_SYSTEM_GENERATED_FIELDS = {
    "Address": "https://mhs.example.com",
    "MHS Party Key": PARTY_KEY,
    "Date Approved": "datetime",
    "Date DNS Approved": "None",
    "Date Requested": "datetime",
    "Managing Organization": "ABC1234",
}


@contextmanager
def mock_epr_product_with_message_set_drd() -> (
    Generator[tuple[ModuleType, CpmProduct], Any, None]
):
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
        product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value=PARTY_KEY)
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(entity=product)

        # set up mhs drd questionnaire responses
        mhs_message_set_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        questionnaire_response = mhs_message_set_questionnaire.validate(
            data={
                "MHS SN": "bar",
                "MHS IN": "baz",
                "Interaction ID": "bar:baz",
                "MHS CPA ID": f"{PARTY_KEY}:bar:baz",
                "Unique Identifier": f"{PARTY_KEY}:bar:baz",
            }
        )
        questionnaire_response_2 = mhs_message_set_questionnaire.validate(
            data={
                "MHS SN": "bar2",
                "MHS IN": "baz2",
                "Interaction ID": "bar2:baz2",
                "MHS CPA ID": f"{PARTY_KEY}:bar2:baz2",
                "Unique Identifier": f"{PARTY_KEY}:bar2:baz2",
            },
        )

        # Set up DeviceReferenceData in DB, for dev
        device_reference_data = product.create_device_reference_data(
            name=EprNameTemplate.MESSAGE_SETS.format(party_key=PARTY_KEY),
            environment=Environment.DEV,
        )
        device_reference_data.add_questionnaire_response(questionnaire_response)
        device_reference_data.add_questionnaire_response(questionnaire_response_2)
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data)

        # Set up another DeviceReferenceData in DB, for ref
        device_reference_data2 = product.create_device_reference_data(
            name=EprNameTemplate.MESSAGE_SETS.format(party_key=PARTY_KEY),
            environment=Environment.REF,
        )
        device_reference_data2.add_questionnaire_response(questionnaire_response)
        device_reference_data2.add_questionnaire_response(questionnaire_response_2)
        device_reference_data_repo.write(device_reference_data2)

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


@contextmanager
def mock_epr_product_without_message_set_drd() -> (
    Generator[tuple[ModuleType, CpmProduct], Any, None]
):
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
        product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value=PARTY_KEY)
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(entity=product)

        import api.createDeviceMessageHandlingSystem.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product


def test_index() -> None:
    with mock_epr_product_with_message_set_drd() as (index, product):
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
                    "environment": Environment.DEV,
                },
            }
        )

        # Validate that the response indicates that a resource was created
        assert response["statusCode"] == 201

        _device = json_loads(response["body"])
        device = Device(**_device)
        assert device.product_team_id == product.product_team_id
        assert device.product_id == product.id
        assert is_mhs_device(device)
        assert device.ods_code == ODS_CODE
        assert device.environment == Environment.DEV
        assert device.created_on.date() == datetime.today().date()
        assert device.updated_on.date() == datetime.today().date()
        assert not device.deleted_on

        questionnaire_responses = device.questionnaire_responses["spine_mhs/1"]
        assert len(questionnaire_responses) == 1
        questionnaire_response = questionnaire_responses[0]
        assert len(questionnaire_response.data) == len(QUESTIONNAIRE_DATA) + len(
            QUESTIONNAIRE_DATA_SYSTEM_GENERATED_FIELDS
        )

        # Retrieve the created resource
        repo = DeviceRepository(
            table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
        )
        created_device = repo.read(
            product_team_id=device.product_team_id,
            product_id=device.product_id,
            environment=device.environment,
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
            {
                "product_id": str(PRODUCT_ID),
                "product_team_id": consistent_uuid(1),
                "environment": Environment.DEV,
            },
            "VALIDATION_ERROR",
            400,
        ),
        (
            {"questionnaire_responses": {"spine_mhs": [QUESTIONNAIRE_DATA]}},
            {
                "product_id": str(PRODUCT_ID),
                "product_team_id": "id_that_does_not_exist",
                "environment": Environment.DEV,
            },
            "RESOURCE_NOT_FOUND",
            404,
        ),
    ],
)
def test_incoming_errors(body, path_parameters, error_code, status_code):
    with mock_epr_product_with_message_set_drd() as (index, _):
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
            "You must provide exactly one spine_mhs questionnaire response to create an MHS Device.",
            400,
        ),
        (
            {
                "questionnaire_responses": {
                    "spine_mhs": [{"MHS FQDN": "mhs.example.com"}]
                }
            },
            "MISSING_VALUE",
            "Failed to validate data against 'spine_mhs/1': 'MHS Manufacturer Organisation' is a required property",
            400,
        ),
        (
            {
                "questionnaire_responses": {
                    "spine_mhs": [{"MHS Manufacturer Organisation": "F5H1R"}]
                }
            },
            "VALIDATION_ERROR",
            "The following required fields are missing in the response to spine_mhs: MHS FQDN",
            400,
        ),
    ],
)
def test_questionnaire_response_validation_errors(
    body, error_code, error_message, status_code
):
    with mock_epr_product_with_message_set_drd() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(body),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                    "environment": Environment.DEV,
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
                    "environment": Environment.DEV,
                },
            }
        )

        assert response["statusCode"] == 400
        expected_error_code = "VALIDATION_ERROR"
        expected_message_code = "Not an EPR Product: Cannot create MHS Device for product without exactly one Party Key"
        assert expected_error_code in response["body"]
        assert expected_message_code in response["body"]


def test_no_existing_message_set_drd():
    with mock_epr_product_without_message_set_drd() as (index, product):
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
                    "environment": Environment.DEV,
                },
            }
        )

        assert response["statusCode"] == 400
        expected_error_code = "VALIDATION_ERROR"
        expected_message_code = "You must configure exactly one MessageSet Device Reference Data before creating an MHS Device"
        assert expected_error_code in response["body"]
        assert expected_message_code in response["body"]


def test_mhs_already_exists() -> None:
    with mock_epr_product_with_message_set_drd() as (index, product):
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
                    "environment": Environment.DEV,
                },
            }
        )

        assert response["statusCode"] == 201

        # Execute the lambda again
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {"questionnaire_responses": {"spine_mhs": [QUESTIONNAIRE_DATA]}}
                ),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                    "environment": Environment.DEV,
                },
            }
        )

        assert response["statusCode"] == 400
        expected_error_code = "VALIDATION_ERROR"
        expected_message_code = (
            "There is already an existing MHS Device for this Product"
        )
        assert expected_error_code in response["body"]
        assert expected_message_code in response["body"]


# Currently this test will break.  But it has been left in for when we decide to fix it.
# def test_mhs_of_differing_envs_allowed() -> None:
#     with mock_epr_product_with_message_set_drd() as (index, product):
#         # Execute the lambda
#         response1 = index.handler(
#             event={
#                 "headers": {"version": VERSION},
#                 "body": json.dumps(
#                     {"questionnaire_responses": {"spine_mhs": [QUESTIONNAIRE_DATA]}}
#                 ),
#                 "pathParameters": {
#                     "product_team_id": str(product.product_team_id),
#                     "product_id": str(product.id),
#                     "environment": Environment.DEV,
#                 },
#             }
#         )
#
#         # Validate that the response indicates that a resource was created
#         assert response1["statusCode"] == 201
#
#         _device1 = json_loads(response1["body"])
#         device1 = Device(**_device1)
#         assert device1.environment == Environment.DEV
#
#         # Retrieve the created resources
#         repo = DeviceRepository(
#             table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
#         )
#
#         created_device1 = repo.read(
#             product_team_id=device1.product_team_id,
#             product_id=device1.product_id,
#             environment=device1.environment,
#             id=device1.id,
#         )
#         # print(created_device1)
#
#         assert created_device1.environment == "dev"
#
#         # Execute the lambda again with ref as the environment
#         response2 = index.handler(
#             event={
#                 "headers": {"version": VERSION},
#                 "body": json.dumps(
#                     {"questionnaire_responses": {"spine_mhs": [QUESTIONNAIRE_DATA]}}
#                 ),
#                 "pathParameters": {
#                     "product_team_id": str(product.product_team_id),
#                     "product_id": str(product.id),
#                     "environment": Environment.REF,
#                 },
#             }
#         )
#         # print(response2)
#         # Validate that the response indicates that a resource was created
#         assert response2["statusCode"] == 201
#
#         _device2 = json_loads(response2["body"])
#         device2 = Device(**_device2)
#         assert device2.environment == Environment.REF
#
#         created_device2 = repo.read(
#             product_team_id=device2.product_team_id,
#             product_id=device2.product_id,
#             environment=device2.environment,
#             id=device2.id,
#         )
#
#         assert created_device2.environment == "ref"
