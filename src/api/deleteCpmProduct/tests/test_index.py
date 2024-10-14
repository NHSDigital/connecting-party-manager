import os
from contextlib import contextmanager
from datetime import datetime
from unittest import mock
from uuid import UUID

import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.cpm_system_id.v1 import ProductId
from domain.core.enum import Status
from domain.core.root.v3 import Root
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.errors import ItemNotFound
from domain.repository.keys.v3 import TableKey
from domain.repository.marshall import marshall, unmarshall
from domain.repository.product_team_repository.v2 import ProductTeamRepository

from test_helpers.dynamodb import mock_table
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"

ODS_CODE = "AAA"
PRODUCT_TEAM_ID = consistent_uuid(1)
PRODUCT_ID = "P.AAA-AAA"
PRODUCT_NAME = "My Product"
VERSION = 1


class MockCpmProductRepository(CpmProductRepository):
    def read_inactive_product(
        self, product_team_id: str, product_id: str
    ) -> CpmProduct:
        pk = TableKey.CPM_PRODUCT_STATUS.key(Status.INACTIVE, product_team_id)
        sk = TableKey.CPM_PRODUCT.key(product_id)
        args = {
            "TableName": self.table_name,
            "KeyConditionExpression": "pk = :pk AND sk = :sk",
            "ExpressionAttributeValues": marshall(**{":pk": pk, ":sk": sk}),
        }
        result = self.client.query(**args)
        items = [unmarshall(i) for i in result["Items"]]
        if len(items) == 0:
            raise ItemNotFound(product_team_id, product_id, item_type=CpmProduct)
        (item,) = items

        return CpmProduct(**item)


@contextmanager
def mock_lambda():
    org = Root.create_ods_organisation(ods_code=ODS_CODE)
    product_team = org.create_product_team(id=PRODUCT_TEAM_ID, name=PRODUCT_NAME)

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

        import api.deleteCpmProduct.index as index

        index.cache["DYNAMODB_CLIENT"] = client

        yield index


def test_index():
    with mock_lambda() as index:
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "pathParameters": {
                    "product_team_id": PRODUCT_TEAM_ID,
                    "product_id": PRODUCT_ID,
                },
            }
        )

        # Validate that the response indicates that a resource was deleted
        assert response["statusCode"] == 204

        # Retrieve the created resource
        repo = CpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
        )
        with pytest.raises(ItemNotFound):
            repo.read(product_team_id=PRODUCT_TEAM_ID, product_id=PRODUCT_ID)

        repo = MockCpmProductRepository(
            table_name=TABLE_NAME, dynamodb_client=index.cache["DYNAMODB_CLIENT"]
        )
        deleted_product = repo.read_inactive_product(
            product_team_id=PRODUCT_TEAM_ID, product_id=PRODUCT_ID
        ).dict()

    # Sense checks on the deleted resource
    created_on = deleted_product.pop("created_on")
    updated_on = deleted_product.pop("updated_on")
    deleted_on = deleted_product.pop("deleted_on")
    assert created_on < updated_on
    assert updated_on == deleted_on
    assert isinstance(created_on, datetime)
    assert isinstance(updated_on, datetime)
    assert isinstance(deleted_on, datetime)

    assert ProductId.validate_cpm_system_id(deleted_product.pop("id"))
    assert deleted_product == {
        "name": PRODUCT_NAME,
        "ods_code": ODS_CODE,
        "product_team_id": UUID(PRODUCT_TEAM_ID),
        "status": Status.INACTIVE,
        "keys": [],
    }


@pytest.mark.parametrize(
    ["path_parameters", "error_code", "status_code"],
    [
        (
            {"product_team_id": PRODUCT_TEAM_ID},
            "MISSING_VALUE",
            400,
        ),
        (
            {"product_id": PRODUCT_ID},
            "MISSING_VALUE",
            400,
        ),
        (
            {
                "product_team_id": PRODUCT_TEAM_ID,
                "product_id": PRODUCT_ID,
                "extra_forbidden_param": "foo",
            },
            "VALIDATION_ERROR",
            400,
        ),
        (
            {"product_team_id": "does-not-exist", "product_id": PRODUCT_ID},
            "RESOURCE_NOT_FOUND",
            404,
        ),
        (
            {"product_team_id": PRODUCT_TEAM_ID, "product_id": "does-not-exist"},
            "RESOURCE_NOT_FOUND",
            404,
        ),
    ],
)
def test_incoming_errors(path_parameters, error_code, status_code):
    with mock_lambda() as index:
        # Execute the lambda
        response = index.handler(
            event={
                "headers": {"version": VERSION},
                "pathParameters": path_parameters,
            }
        )

        # Validate that the response indicates that the expected error
        assert response["statusCode"] == status_code
        assert error_code in response["body"]
