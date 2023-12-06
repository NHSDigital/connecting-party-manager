from uuid import UUID

import boto3
import pytest
from domain.core.root import Root
from domain.repository.product_team_repository import ProductTeamRepository

from test_helpers.terraform import read_terraform_output


@pytest.mark.integration
def test__product_team_repository():
    team_id = UUID("359e28eb-6e2c-409c-a3ab-a4868ab5c2df")
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="AB123")
    team = org.create_product_team(id=team_id, name="Test Team")

    repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=boto3.client("dynamodb"),
    )

    response = repo.write(team)

    result = repo.read(team_id)

    assert result is not None, "failed to load"
    assert result.id == team.id, "id"
    assert result.name == team.name, "name"
    assert result.ods_code == team.ods_code, "ods_code"
