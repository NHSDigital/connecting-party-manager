import json
import os
from contextlib import contextmanager
from datetime import datetime
from types import ModuleType
from typing import Any, Generator
from unittest import mock

from domain.core.cpm_product import CpmProduct
from domain.core.cpm_system_id import PartyKeyId, ProductId
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.product_key import ProductKeyType
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.product_team_repository import ProductTeamRepository
from event.json import json_loads

from test_helpers.dynamodb import mock_table

TABLE_NAME = "hiya"

ODS_CODE = "AAA"
PRODUCT_ID = ProductId.create()
PRODUCT_NAME = "My Product"
VERSION = 1


@contextmanager
def mock_product() -> Generator[tuple[ModuleType, CpmProduct], Any, None]:
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(name=PRODUCT_NAME)

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
        product.add_key(
            key_type=ProductKeyType.PARTY_KEY,
            key_value=str(PartyKeyId.create(current_number=100000, ods_code="AAA")),
        )
        product_repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=client
        )
        product_repo.write(entity=product)

        import api.createDeviceReferenceDataMessageSet.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index, product


def test_index_without_questionnaire() -> None:
    with mock_product() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps({}),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                },
            }
        )

        # Validate that the response indicates that a resource was created
        assert response["statusCode"] == 201

        _device_reference_data = json_loads(response["body"])
        device_reference_data = DeviceReferenceData(**_device_reference_data)
        assert device_reference_data.product_id == product.id
        assert device_reference_data.product_team_id == product.product_team_id
        assert device_reference_data.name == "AAA-100001 - MHS Message Sets"
        assert device_reference_data.ods_code == ODS_CODE
        assert device_reference_data.created_on.date() == datetime.today().date()
        assert device_reference_data.updated_on is None
        assert device_reference_data.deleted_on is None
        assert device_reference_data.questionnaire_responses == {}

        # Retrieve the created resource
        repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
        )

        created_device_reference_data = repo.read(
            product_team_id=device_reference_data.product_team_id,
            product_id=device_reference_data.product_id,
            id=device_reference_data.id,
        )
        assert created_device_reference_data == device_reference_data


def test_index_with_questionnaire() -> None:
    questionnaire_data = {
        "Interaction ID": "foo",
        "MHS SN": "bar",
        "MHS IN": "baz",
    }

    with mock_product() as (index, product):
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "body": json.dumps(
                    {
                        "questionnaire_responses": {
                            "spine_mhs_message_sets": [questionnaire_data]
                        }
                    }
                ),
                "pathParameters": {
                    "product_team_id": str(product.product_team_id),
                    "product_id": str(product.id),
                },
            }
        )

        # Validate that the response indicates that a resource was created
        assert response["statusCode"] == 201

        _device_reference_data = json_loads(response["body"])
        device_reference_data = DeviceReferenceData(**_device_reference_data)
        assert device_reference_data.product_id == product.id
        assert device_reference_data.product_team_id == product.product_team_id
        assert device_reference_data.name == "AAA-100001 - MHS Message Sets"
        assert device_reference_data.ods_code == ODS_CODE
        assert device_reference_data.created_on.date() == datetime.today().date()
        assert device_reference_data.updated_on.date() == datetime.today().date()
        assert device_reference_data.deleted_on is None

        questionnaire_responses = device_reference_data.questionnaire_responses[
            "spine_mhs_message_sets/1"
        ]
        assert len(questionnaire_responses) == 1
        questionnaire_response = questionnaire_responses[0]
        assert questionnaire_response.data == questionnaire_data

        # Retrieve the created resource
        repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
        )

        created_device_reference_data = repo.read(
            product_team_id=device_reference_data.product_team_id,
            product_id=device_reference_data.product_id,
            id=device_reference_data.id,
        )
        assert created_device_reference_data == device_reference_data
