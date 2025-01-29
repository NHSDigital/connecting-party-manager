import pytest
from domain.api.common_steps.read_product import before_steps
from domain.core.cpm_product import CpmProduct
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.errors import ItemNotFound
from domain.repository.product_team_epr_repository import ProductTeamRepository
from domain.response.validation_errors import InboundValidationError
from event.step_chain import StepChain

from conftest import dynamodb_client_with_sleep as dynamodb_client
from test_helpers.dynamodb import mock_table
from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID

TABLE_NAME = "my-table"


@pytest.mark.parametrize(
    ["event", "expected_exception"],
    [
        (
            {"pathParameters": {"product_team_id": "does-not-exist"}},
            InboundValidationError,
        ),
        (
            {
                "pathParameters": {
                    "product_team_id": "does-not-exist",
                    "product_id": "does-not-exist",
                },
            },
            ItemNotFound,
        ),
    ],
)
def test_read_product_steps_bad_input(event: dict, expected_exception: type[Exception]):
    step_chain = StepChain(step_chain=before_steps)

    mocked_cache = {"DYNAMODB_CLIENT": dynamodb_client(), "DYNAMODB_TABLE": TABLE_NAME}
    with mock_table(table_name=TABLE_NAME):
        step_chain.run(init=event, cache=mocked_cache)

    assert isinstance(step_chain.result, expected_exception)


def test_read_product_steps_good_input():
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    product_team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )
    ods_code = CPM_PRODUCT_TEAM_NO_ID["ods_code"]
    step_chain = StepChain(step_chain=before_steps)

    mocked_cache = {"DYNAMODB_CLIENT": dynamodb_client(), "DYNAMODB_TABLE": TABLE_NAME}
    with mock_table(table_name=TABLE_NAME):
        product_team_repo = ProductTeamRepository(
            table_name=mocked_cache["DYNAMODB_TABLE"],
            dynamodb_client=mocked_cache["DYNAMODB_CLIENT"],
        )
        product_team_repo.write(product_team)

        product_repo = CpmProductRepository(
            table_name=mocked_cache["DYNAMODB_TABLE"],
            dynamodb_client=mocked_cache["DYNAMODB_CLIENT"],
        )
        product = product_team.create_cpm_product(name="foo-product")
        product_repo.write(product)

        step_chain.run(
            init={
                "pathParameters": {
                    "product_team_id": str(product_team.id),
                    "product_id": str(product.id),
                },
            },
            cache=mocked_cache,
        )

    assert isinstance(step_chain.result, CpmProduct)
    assert step_chain.result.product_team_id == product_team.id
    assert step_chain.result.ods_code == ods_code
