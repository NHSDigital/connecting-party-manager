import json
from uuid import uuid4

import pytest
from domain.common_steps.create_product import before_steps
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.root.v2 import Root
from domain.repository.errors import ItemNotFound
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from domain.response.validation_errors import (
    InboundJSONDecodeError,
    InboundValidationError,
)
from event.aws.client import dynamodb_client
from event.step_chain import StepChain

from test_helpers.dynamodb import mock_table

TABLE_NAME = "my-table"


@pytest.mark.parametrize(
    ["event", "expected_exception"],
    [
        (
            {
                "body": "not:json",
                "pathParameters": {"product_team_id": "does-not-exist"},
            },
            InboundJSONDecodeError,
        ),
        (
            {
                "body": json.dumps({"invalid": "data"}),
                "pathParameters": {"product_team_id": "does-not-exist"},
            },
            InboundValidationError,
        ),
        (
            {
                "body": json.dumps({"product_name": "foo"}),
                "pathParameters": {"product_team_id": "does-not-exist"},
            },
            ItemNotFound,
        ),
    ],
)
def test_create_product_steps_bad_input(
    event: dict, expected_exception: type[Exception]
):
    step_chain = StepChain(step_chain=before_steps)

    mocked_cache = {"DYNAMODB_CLIENT": dynamodb_client(), "DYNAMODB_TABLE": TABLE_NAME}
    with mock_table(table_name=TABLE_NAME):
        step_chain.run(init=event, cache=mocked_cache)

    assert isinstance(step_chain.result, expected_exception)


def test_create_product_steps_good_input():
    product_team_id = uuid4()
    ods_code = "AAA"
    product_name = "foo"
    event = {
        "body": json.dumps({"product_name": product_name}),
        "pathParameters": {"product_team_id": str(product_team_id)},
    }

    step_chain = StepChain(step_chain=before_steps)

    mocked_cache = {"DYNAMODB_CLIENT": dynamodb_client(), "DYNAMODB_TABLE": TABLE_NAME}
    with mock_table(table_name=TABLE_NAME):
        product_team_repo = ProductTeamRepository(
            table_name=mocked_cache["DYNAMODB_TABLE"],
            dynamodb_client=mocked_cache["DYNAMODB_CLIENT"],
        )
        org = Root.create_ods_organisation(ods_code=ods_code)
        product_team = org.create_product_team(id=product_team_id, name="foo-team")
        product_team_repo.write(product_team)
        step_chain.run(init=event, cache=mocked_cache)

    assert isinstance(step_chain.result, CpmProduct)
    assert step_chain.result.product_team_id == product_team_id
    assert step_chain.result.ods_code == ods_code
