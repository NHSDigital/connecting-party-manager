import json
import os
from contextlib import contextmanager
from datetime import datetime
from types import ModuleType
from typing import Any, Generator
from unittest import mock

from domain.core.cpm_system_id import ProductId
from domain.core.device_reference_data import DeviceReferenceData
from domain.core.enum import Environment
from domain.core.epr_product import EprProduct
from domain.core.product_key import ProductKeyType
from domain.core.root import Root
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from event.json import json_loads

from test_helpers.dynamodb import mock_table

TABLE_NAME = "hiya"

ODS_CODE = "AAA"
PRODUCT_ID = ProductId.create()
PRODUCT_NAME = "My Product"
VERSION = 1
PARTY_KEY = "AAA-100001"


@contextmanager
def mock_product() -> Generator[tuple[ModuleType, EprProduct], Any, None]:
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team_epr(name=PRODUCT_NAME)

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
        product.add_key(key_type=ProductKeyType.PARTY_KEY, key_value=PARTY_KEY),

        product_repo = EprProductRepository(
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
                    "environment": Environment.DEV,
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
        assert device_reference_data.environment == Environment.DEV
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
            environment=device_reference_data.environment,
            id=device_reference_data.id,
        )
        assert created_device_reference_data == device_reference_data


def test_index_with_questionnaire() -> None:
    questionnaire_data = {
        "MHS SN": "bar",
        "MHS IN": "baz",
    }
    questionnaire_data_with_generated_fields = {
        "MHS SN": "bar",
        "MHS IN": "baz",
        "Interaction ID": "bar:baz",
        "MHS CPA ID": f"{PARTY_KEY}:bar:baz",
        "Unique Identifier": f"{PARTY_KEY}:bar:baz",
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
                    "environment": Environment.DEV,
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
        assert device_reference_data.environment == Environment.DEV
        assert device_reference_data.created_on.date() == datetime.today().date()
        assert device_reference_data.updated_on.date() == datetime.today().date()
        assert device_reference_data.deleted_on is None

        questionnaire_responses = device_reference_data.questionnaire_responses[
            "spine_mhs_message_sets/1"
        ]
        assert len(questionnaire_responses) == 1
        questionnaire_response = questionnaire_responses[0]
        assert questionnaire_response.data == questionnaire_data_with_generated_fields

        # Retrieve the created resource
        repo = DeviceReferenceDataRepository(
            table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
        )

        created_device_reference_data = repo.read(
            product_team_id=device_reference_data.product_team_id,
            product_id=device_reference_data.product_id,
            environment=device_reference_data.environment,
            id=device_reference_data.id,
        )
        assert created_device_reference_data == device_reference_data
