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
from domain.core.device_key.v1 import DeviceKey, DeviceKeyType
from domain.core.product_key import ProductKeyType
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.device_repository import DeviceRepository
from domain.repository.product_team_repository import ProductTeamRepository
from domain.repository.questionnaire_repository import (
    QuestionnaireInstance,
    QuestionnaireRepository,
)
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"
DEVICE_NAME = "Product-AS"
ODS_CODE = "AAA"
PRODUCT_ID = ProductId.create()
PRODUCT_TEAM_NAME = "My Product Team"
PRODUCT_NAME = "My Product"
VERSION = 1
PARTY_KEY = "ABC1234-987654"

QUESTIONNAIRE_DATA = {
    "ODS Code": "FH15R",
    "Client ODS Codes": ["FH15R"],
    "ASID": "foobar",
    "Party Key": "P.123-XXX",
    "Approver URP": "approver-123",
    "Date Approved": "2024-01-01",
    "Requestor URP": "requestor-789",
    "Date Requested": "2024-01-03",
    "Product Key": "product-key-001",
}


@contextmanager
def mock_epr_product_with_one_message_set_drd() -> (
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

        mhs_message_set_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        questionnaire_response_1 = mhs_message_set_questionnaire.validate(
            data={
                "Interaction ID": "bar:baz",
                "MHS SN": "bar",
                "MHS IN": "baz",
                "MHS CPA ID": f"{PARTY_KEY}:bar:baz",
                "Unique Identifier": f"{PARTY_KEY}:bar:baz",
            }
        )
        questionnaire_response_2 = mhs_message_set_questionnaire.validate(
            data={
                "Interaction ID": "bar2:baz2",
                "MHS SN": "bar2",
                "MHS IN": "baz2",
                "MHS CPA ID": f"{PARTY_KEY}:bar2:baz2",
                "Unique Identifier": f"{PARTY_KEY}:bar2:baz2",
            }
        )

        # Set up DeviceReferenceData in DB
        device_reference_data_mhs = product.create_device_reference_data(
            name="ABC1234-987654 - MHS Message Set"
        )
        device_reference_data_mhs.add_questionnaire_response(questionnaire_response_1)
        device_reference_data_mhs.add_questionnaire_response(questionnaire_response_2)

        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data_mhs)

        import api.createDeviceAccreditedSystem.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product


@contextmanager
def mock_epr_product_with_message_sets_drd() -> (
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

        mhs_message_set_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )

        questionnaire_response_1 = mhs_message_set_questionnaire.validate(
            data={
                "Interaction ID": "bar:baz",
                "MHS SN": "bar",
                "MHS IN": "baz",
                "MHS CPA ID": f"{PARTY_KEY}:bar:baz",
                "Unique Identifier": f"{PARTY_KEY}:bar:baz",
            }
        )
        questionnaire_response_2 = mhs_message_set_questionnaire.validate(
            data={
                "Interaction ID": "bar2:baz2",
                "MHS SN": "bar2",
                "MHS IN": "baz2",
                "MHS CPA ID": f"{PARTY_KEY}:bar2:baz2",
                "Unique Identifier": f"{PARTY_KEY}:bar2:baz2",
            }
        )
        # Set up DeviceReferenceData in DB
        device_reference_data_mhs = product.create_device_reference_data(
            name="ABC1234-987654 - MHS Message Set"
        )
        device_reference_data_mhs.add_questionnaire_response(questionnaire_response_1)
        device_reference_data_mhs.add_questionnaire_response(questionnaire_response_2)

        # set up questionnaire response
        as_additional_interactions_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        )
        questionnaire_response_3 = as_additional_interactions_questionnaire.validate(
            data={"Interaction ID": "urn:foo3"}
        )
        questionnaire_response_4 = as_additional_interactions_questionnaire.validate(
            data={"Interaction ID": "urn:foo4"}
        )

        # Set up DeviceReferenceData in DB
        device_reference_data_as = product.create_device_reference_data(
            name="ABC1234-987654 - AS Additional Interactions"
        )
        device_reference_data_as.add_questionnaire_response(questionnaire_response_3)
        device_reference_data_as.add_questionnaire_response(questionnaire_response_4)
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data_as)
        device_reference_data_repo.write(device_reference_data_mhs)

        import api.createDeviceAccreditedSystem.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product


@contextmanager
def mock_epr_product_with_more_than_two_message_sets_drd() -> (
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

        mhs_message_set_questionnaire_1 = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        questionnaire_response_1 = mhs_message_set_questionnaire_1.validate(
            data={
                "Interaction ID": "bar:baz",
                "MHS SN": "bar",
                "MHS IN": "baz",
                "MHS CPA ID": f"{PARTY_KEY}:bar:baz",
                "Unique Identifier": f"{PARTY_KEY}:bar:baz",
            }
        )
        questionnaire_response_2 = mhs_message_set_questionnaire_1.validate(
            data={
                "Interaction ID": "bar2:baz2",
                "MHS SN": "bar2",
                "MHS IN": "baz2",
                "MHS CPA ID": f"{PARTY_KEY}:bar2:baz2",
                "Unique Identifier": f"{PARTY_KEY}:bar2:baz2",
            }
        )

        # Set up DeviceReferenceData in DB
        device_reference_data_mhs_1 = product.create_device_reference_data(
            name="ABC1234-987654 - MHS Message Set"
        )
        device_reference_data_mhs_1.add_questionnaire_response(questionnaire_response_1)
        device_reference_data_mhs_1.add_questionnaire_response(questionnaire_response_2)

        mhs_message_set_questionnaire_2 = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        questionnaire_response_3 = mhs_message_set_questionnaire_2.validate(
            data={
                "Interaction ID": "bar3:baz3",
                "MHS SN": "bar3",
                "MHS IN": "baz3",
                "MHS CPA ID": f"{PARTY_KEY}:bar3:baz3",
                "Unique Identifier": f"{PARTY_KEY}:bar3:baz3",
            }
        )
        questionnaire_response_4 = mhs_message_set_questionnaire_2.validate(
            data={
                "Interaction ID": "bar4:baz4",
                "MHS SN": "bar4",
                "MHS IN": "baz4",
                "MHS CPA ID": f"{PARTY_KEY}:bar4:baz4",
                "Unique Identifier": f"{PARTY_KEY}:bar4:baz4",
            }
        )

        # Set up DeviceReferenceData in DB
        device_reference_data_mhs_2 = product.create_device_reference_data(
            name="ABC1234-987654 - MHS Message Set"
        )
        device_reference_data_mhs_2.add_questionnaire_response(questionnaire_response_3)
        device_reference_data_mhs_2.add_questionnaire_response(questionnaire_response_4)
        # set up questionnaire response
        as_additional_interactions_questionnaire = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS
        )
        questionnaire_response_5 = as_additional_interactions_questionnaire.validate(
            data={"Interaction ID": "urn:foo5"}
        )
        questionnaire_response_6 = as_additional_interactions_questionnaire.validate(
            data={"Interaction ID": "urn:foo6"}
        )

        # Set up DeviceReferenceData in DB
        device_reference_data_as = product.create_device_reference_data(
            name="ABC1234-987654 - AS Additional Interactions"
        )
        device_reference_data_as.add_questionnaire_response(questionnaire_response_5)
        device_reference_data_as.add_questionnaire_response(questionnaire_response_6)
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data_as)
        device_reference_data_repo.write(device_reference_data_mhs_1)
        device_reference_data_repo.write(device_reference_data_mhs_2)

        import api.createDeviceAccreditedSystem.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product


@contextmanager
def mock_epr_product_with_two_message_sets_the_same_drd() -> (
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

        mhs_message_set_questionnaire_1 = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        questionnaire_response_1 = mhs_message_set_questionnaire_1.validate(
            data={
                "Interaction ID": "bar:baz",
                "MHS SN": "bar",
                "MHS IN": "baz",
                "MHS CPA ID": f"{PARTY_KEY}:bar:baz",
                "Unique Identifier": f"{PARTY_KEY}:bar:baz",
            }
        )
        questionnaire_response_2 = mhs_message_set_questionnaire_1.validate(
            data={
                "Interaction ID": "bar2:baz2",
                "MHS SN": "ba2r",
                "MHS IN": "baz2",
                "MHS CPA ID": f"{PARTY_KEY}:bar2:baz2",
                "Unique Identifier": f"{PARTY_KEY}:bar2:baz2",
            }
        )

        # Set up DeviceReferenceData in DB
        device_reference_data_mhs_1 = product.create_device_reference_data(
            name="ABC1234-987654 - MHS Message Set"
        )
        device_reference_data_mhs_1.add_questionnaire_response(questionnaire_response_1)
        device_reference_data_mhs_1.add_questionnaire_response(questionnaire_response_2)

        mhs_message_set_questionnaire_2 = QuestionnaireRepository().read(
            QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS
        )
        questionnaire_response_3 = mhs_message_set_questionnaire_2.validate(
            data={
                "Interaction ID": "bar3:baz3",
                "MHS SN": "bar3",
                "MHS IN": "baz3",
                "MHS CPA ID": f"{PARTY_KEY}:bar3:baz3",
                "Unique Identifier": f"{PARTY_KEY}:bar3:baz3",
            }
        )
        questionnaire_response_4 = mhs_message_set_questionnaire_2.validate(
            data={
                "Interaction ID": "bar4:baz4",
                "MHS SN": "bar4",
                "MHS IN": "baz4",
                "MHS CPA ID": f"{PARTY_KEY}:bar4:baz4",
                "Unique Identifier": f"{PARTY_KEY}:bar4:baz4",
            }
        )

        # Set up DeviceReferenceData in DB
        device_reference_data_mhs_2 = product.create_device_reference_data(
            name="ABC1234-987654 - MHS Message Set"
        )
        device_reference_data_mhs_2.add_questionnaire_response(questionnaire_response_3)
        device_reference_data_mhs_2.add_questionnaire_response(questionnaire_response_4)
        # set up questionnaire response
        device_reference_data_repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        device_reference_data_repo.write(device_reference_data_mhs_1)
        device_reference_data_repo.write(device_reference_data_mhs_2)

        import api.createDeviceAccreditedSystem.index as index

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

        import api.createDeviceAccreditedSystem.index as index

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

        import api.createDeviceAccreditedSystem.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product


def test_index() -> None:
    with mock_epr_product_with_message_sets_drd() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {"questionnaire_responses": {"spine_as": [QUESTIONNAIRE_DATA]}}
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
        assert device.name == "ABC1234-987654/200000100000 - Accredited System"
        assert device.ods_code == ODS_CODE
        assert device.created_on.date() == datetime.today().date()
        assert device.updated_on.date() == datetime.today().date()
        assert device.deleted_on is None

        # print(device.questionnaire_responses)
        questionnaire_responses = device.questionnaire_responses["spine_as/1"]
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
        expected_party_key = (str(ProductKeyType.PARTY_KEY), PARTY_KEY.lower())
        assert any(expected_party_key in tag.__root__ for tag in created_device.tags)

        # Check an ASID is generated and added to the keys.
        assert isinstance(created_device.keys[0], DeviceKey)
        assert created_device.keys[0].__dict__ == {
            "key_type": DeviceKeyType.ACCREDITED_SYSTEM_ID,
            "key_value": "200000100000",
        }


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
            {"questionnaire_responses": {"spine_as": [QUESTIONNAIRE_DATA]}},
            {},
            "MISSING_VALUE",
            400,
        ),
        (
            {
                "questionnaire_responses": {"spine_as": [QUESTIONNAIRE_DATA]},
                "forbidden_extra_param": "urn:foo",
            },
            {"product_id": str(PRODUCT_ID), "product_team_id": consistent_uuid(1)},
            "VALIDATION_ERROR",
            400,
        ),
        (
            {"questionnaire_responses": {"spine_as": [QUESTIONNAIRE_DATA]}},
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
    with mock_epr_product_with_message_sets_drd() as (index, _):
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
                    "spine_as": [QUESTIONNAIRE_DATA, QUESTIONNAIRE_DATA]
                },
            },
            "VALIDATION_ERROR",
            "CreateAsDeviceIncomingParams.questionnaire_responses.spine_as.__root__: ensure this value has at most 1 items",
            400,
        ),
        (
            {
                "questionnaire_responses": {
                    "spine_as": [{"Address": "http://example.com"}]
                }
            },
            "MISSING_VALUE",
            "Failed to validate data against 'spine_as/1': 'Party Key' is a required property",
            400,
        ),
    ],
)
def test_questionnaire_response_validation_errors(
    body, error_code, error_message, status_code
):
    with mock_epr_product_with_message_sets_drd() as (index, product):
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


def test_all_mhs_message_sets():
    with mock_epr_product_with_two_message_sets_the_same_drd() as (index, product):
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {"questionnaire_responses": {"spine_as": [QUESTIONNAIRE_DATA]}}
                ),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                },
            }
        )

        assert response["statusCode"] == 400
        expected_error_code = "VALIDATION_ERROR"
        expected_message_code = "Only one AS and one MessageSet Device Reference Data is allowed before creating an AS Device"
        assert expected_error_code in response["body"]
        assert expected_message_code in response["body"]


def test_not_epr_product():
    with mock_not_epr_product() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {"questionnaire_responses": {"spine_as": [QUESTIONNAIRE_DATA]}}
                ),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                },
            }
        )

        assert response["statusCode"] == 400
        expected_error_code = "VALIDATION_ERROR"
        expected_message_code = "Not an EPR Product: Cannot create AS device for product without exactly one Party Key"
        assert expected_error_code in response["body"]
        assert expected_message_code in response["body"]


def test_no_existing_message_set_drd():
    with mock_epr_product_without_message_set_drd() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {"questionnaire_responses": {"spine_as": [QUESTIONNAIRE_DATA]}}
                ),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                },
            }
        )

        assert response["statusCode"] == 400
        expected_error_code = "VALIDATION_ERROR"
        expected_message_code = "You must configure the AS and MessageSet Device Reference Data before creating an AS Device"
        assert expected_error_code in response["body"]
        assert expected_message_code in response["body"]


def test_less_than_2_existing_message_set_drd():
    with mock_epr_product_with_one_message_set_drd() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {"questionnaire_responses": {"spine_as": [QUESTIONNAIRE_DATA]}}
                ),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                },
            }
        )

        assert response["statusCode"] == 400
        expected_error_code = "VALIDATION_ERROR"
        expected_message_code = "You must configure the AS and MessageSet Device Reference Data before creating an AS Device"
        assert expected_error_code in response["body"]
        assert expected_message_code in response["body"]


def test_too_many_message_sets_drd():
    with mock_epr_product_with_more_than_two_message_sets_drd() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {"questionnaire_responses": {"spine_as": [QUESTIONNAIRE_DATA]}}
                ),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                },
            }
        )

        assert response["statusCode"] == 400
        expected_error_code = "VALIDATION_ERROR"
        expected_message_code = "More that 2 MessageSet Device Reference Data resources were found. This is not allowed"
        assert expected_error_code in response["body"]
        assert expected_message_code in response["body"]
