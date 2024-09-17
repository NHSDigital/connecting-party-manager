import pytest
from domain.core.root import Root
from domain.repository.errors import AlreadyExistsError, ItemNotFound
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from event.aws.client import dynamodb_client

from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output


@pytest.mark.integration
def test__product_team_repository():
    team_id = "359e28eb-6e2c-409c-a3ab-a4868ab5c2df"
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(id=team_id, name="Test Team")

    repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

    repo.write(team)
    result = repo.read(team_id)
    assert result == team


@pytest.mark.integration
def test__product_team_repository_already_exists():
    team_id = "359e28eb-6e2c-409c-a3ab-a4868ab5c2df"
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(id=team_id, name="Test Team")
    repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

    repo.write(team)
    with pytest.raises(AlreadyExistsError):
        repo.write(team)


@pytest.mark.integration
def test__product_team_repository__device_does_not_exist():
    team_id = "359e28eb-6e2c-409c-a3ab-a4868ab5c2df"
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )
    with pytest.raises(ItemNotFound):
        repo.read(team_id)


def test__product_team_repository_local():
    team_id = "359e28eb-6e2c-409c-a3ab-a4868ab5c2df"

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(id=team_id, name="Test Team")

    with mock_table("my_table") as client:
        repo = ProductTeamRepository(
            table_name="my_table",
            dynamodb_client=client,
        )

        repo.write(team)
        result = repo.read(team_id)
    assert result == team


def test__product_team_repository__device_does_not_exist_local():
    team_id = "359e28eb-6e2c-409c-a3ab-a4868ab5c2df"

    with mock_table("my_table") as client:
        repo = ProductTeamRepository(
            table_name="my_table",
            dynamodb_client=client,
        )
        with pytest.raises(ItemNotFound):
            repo.read(team_id)
