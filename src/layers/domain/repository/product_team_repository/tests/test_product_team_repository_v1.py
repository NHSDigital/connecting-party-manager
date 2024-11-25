import pytest
from domain.core.root import Root
from domain.repository.errors import AlreadyExistsError, ItemNotFound
from domain.repository.product_team_repository import ProductTeamRepository
from event.aws.client import dynamodb_client

from test_helpers.dynamodb import mock_table
from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID
from test_helpers.terraform import read_terraform_output


@pytest.mark.integration
def test__product_team_repository():
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )

    repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

    repo.write(team)
    team_id = team.id
    result = repo.read(team_id)
    assert result == team


@pytest.mark.integration
def test__product_team_repository_already_exists():
    table_name = read_terraform_output("dynamodb_table_name.value")
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )

    repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )
    repo.write(team)
    with pytest.raises(AlreadyExistsError):
        repo.write(team)


@pytest.mark.integration
def test__product_team_repository__product_team_does_not_exist():
    team_id = (
        f"{CPM_PRODUCT_TEAM_NO_ID["ods_code"]}.359e28eb-6e2c-409c-a3ab-a4868ab5c2df"
    )
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )
    with pytest.raises(ItemNotFound):
        repo.read(team_id)


def test__product_team_repository_local():
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    team = org.create_product_team(
        name="Test Team", keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )
    team_id = team.id

    with mock_table("my_table") as client:
        repo = ProductTeamRepository(
            table_name="my_table",
            dynamodb_client=client,
        )

        repo.write(team)
        result = repo.read(team_id)
    assert result.state() == team.state()


def test__product_team_repository__product_team_does_not_exist_local():
    team_id = "359e28eb-6e2c-409c-a3ab-a4868ab5c2df"

    with mock_table("my_table") as client:
        repo = ProductTeamRepository(
            table_name="my_table",
            dynamodb_client=client,
        )
        with pytest.raises(ItemNotFound):
            repo.read(team_id)
