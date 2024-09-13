import json
<<<<<<< HEAD
from uuid import uuid4
=======
>>>>>>> 86bfcdd (release/2024-09-13 Create release branch)

import pytest
from domain.common_steps.create_product import before_steps
from domain.core.cpm_product.v1 import CpmProduct
<<<<<<< HEAD
from domain.core.root.v2 import Root
=======
from domain.core.root.v3 import Root
>>>>>>> 86bfcdd (release/2024-09-13 Create release branch)
from domain.repository.errors import ItemNotFound
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from domain.response.validation_errors import (
    InboundJSONDecodeError,
    InboundValidationError,
)
from event.aws.client import dynamodb_client
from event.step_chain import StepChain

from test_helpers.dynamodb import mock_table
<<<<<<< HEAD
=======
from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID
>>>>>>> 86bfcdd (release/2024-09-13 Create release branch)

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
<<<<<<< HEAD
    product_team_id = uuid4()
    ods_code = "AAA"
    product_name = "foo"
    event = {
        "body": json.dumps({"product_name": product_name}),
        "pathParameters": {"product_team_id": str(product_team_id)},
=======
    ods_code = CPM_PRODUCT_TEAM_NO_ID["ods_code"]
    product_name = "foo"
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    product_team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )
    event = {
        "body": json.dumps({"product_name": product_name}),
        "pathParameters": {"product_team_id": str(product_team.id)},
>>>>>>> 86bfcdd (release/2024-09-13 Create release branch)
    }

    step_chain = StepChain(step_chain=before_steps)

    mocked_cache = {"DYNAMODB_CLIENT": dynamodb_client(), "DYNAMODB_TABLE": TABLE_NAME}
    with mock_table(table_name=TABLE_NAME):
        product_team_repo = ProductTeamRepository(
            table_name=mocked_cache["DYNAMODB_TABLE"],
            dynamodb_client=mocked_cache["DYNAMODB_CLIENT"],
        )
<<<<<<< HEAD
        org = Root.create_ods_organisation(ods_code=ods_code)
        product_team = org.create_product_team(id=product_team_id, name="foo-team")
=======
>>>>>>> 86bfcdd (release/2024-09-13 Create release branch)
        product_team_repo.write(product_team)
        step_chain.run(init=event, cache=mocked_cache)

    assert isinstance(step_chain.result, CpmProduct)
<<<<<<< HEAD
    assert step_chain.result.product_team_id == product_team_id
=======
    assert step_chain.result.product_team_id == product_team.id
>>>>>>> 86bfcdd (release/2024-09-13 Create release branch)
    assert step_chain.result.ods_code == ods_code
