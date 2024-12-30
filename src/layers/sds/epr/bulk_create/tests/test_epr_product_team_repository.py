from random import shuffle

import pytest
from domain.core.product_team.v1 import ProductTeam
from domain.core.product_team_key.v1 import ProductTeamKey, ProductTeamKeyType
from sds.epr.bulk_create.bulk_repository import BulkRepository
from sds.epr.bulk_create.epr_product_team_repository import EprProductTeamRepository

from conftest import dynamodb_client_with_sleep as _dynamodb_client
from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output

TABLE_NAME = "my-table"


@pytest.fixture
def dynamodb_client():
    with mock_table(TABLE_NAME) as client:
        yield client


def test_get_all_epr_product_teams_local(dynamodb_client):
    epr_ods_codes = [f"AAA{i}" for i in range(1034)]
    epr_product_teams = [
        ProductTeam(
            name=ods_code,
            ods_code=ods_code,
            keys=[
                ProductTeamKey(
                    key_type=ProductTeamKeyType.EPR_ID, key_value=f"EPR-{ods_code}"
                )
            ],
        )
        for ods_code in epr_ods_codes
    ]
    non_epr_product_teams = [
        ProductTeam(name=str(i), ods_code="AAA") for i in range(2483)
    ]

    product_teams = [*epr_product_teams, *non_epr_product_teams]
    shuffle(product_teams)

    repo = BulkRepository(table_name="my-table", dynamodb_client=dynamodb_client)
    transactions = []
    for product_team in product_teams:
        transactions += repo.generate_transaction_statements(
            {"ProductTeam": product_team.state()}
        )
    repo.write(transactions)

    epr_product_team_repo = EprProductTeamRepository(
        table_name="my-table", dynamodb_client=dynamodb_client
    )
    product_teams_from_db = list(epr_product_team_repo.search())
    assert len(product_teams_from_db) == len(epr_ods_codes)


@pytest.mark.integration
def test_get_all_epr_product_teams():
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = _dynamodb_client()

    epr_ods_codes = [f"AAA{i}" for i in range(103)]
    epr_product_teams = [
        ProductTeam(
            name=ods_code,
            ods_code=ods_code,
            keys=[
                ProductTeamKey(
                    key_type=ProductTeamKeyType.EPR_ID, key_value=f"EPR-{ods_code}"
                )
            ],
        )
        for ods_code in epr_ods_codes
    ]
    non_epr_product_teams = [
        ProductTeam(name=str(i), ods_code="AAA") for i in range(248)
    ]

    product_teams = [*epr_product_teams, *non_epr_product_teams]
    shuffle(product_teams)

    repo = BulkRepository(table_name=table_name, dynamodb_client=client)
    transactions = []
    for product_team in product_teams:
        transactions += repo.generate_transaction_statements(
            {"ProductTeam": product_team.state()}
        )
    repo.write(transactions)

    epr_product_team_repo = EprProductTeamRepository(
        table_name=table_name, dynamodb_client=client
    )
    product_teams_from_db = list(epr_product_team_repo.search())
    assert len(product_teams_from_db) == len(epr_ods_codes)
