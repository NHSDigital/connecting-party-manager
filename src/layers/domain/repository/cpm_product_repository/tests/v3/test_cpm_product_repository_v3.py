import pytest
from domain.core.cpm_system_id.v1 import ProductId
from domain.core.root.v3 import Root
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.errors import AlreadyExistsError, ItemNotFound
from event.aws.client import dynamodb_client

from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output
from test_helpers.uuid import consistent_uuid


@pytest.mark.integration
def test__cpm_product_repository():
    product_id = ProductId.create()
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name"
    )
    cpm_product = product_team.create_cpm_product(
        name="cpm-product-name", product_id=product_id.id
    )

    repo = CpmProductRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

    repo.write(cpm_product)
    result = repo.read(product_team_id=product_team.id, product_id=cpm_product.id.id)
    assert result == cpm_product


@pytest.mark.integration
def test__cpm_product_repository_already_exists():
    product_id = "P.XXX-YYY"
    table_name = read_terraform_output("dynamodb_table_name.value")

    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name"
    )
    cpm_product = product_team.create_cpm_product(
        name="cpm-product-name", product_id=product_id
    )

    repo = CpmProductRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

    repo.write(cpm_product)
    with pytest.raises(AlreadyExistsError):
        repo.write(cpm_product)


@pytest.mark.integration
def test__cpm_product_repository__product_does_not_exist():
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"
    table_name = read_terraform_output("dynamodb_table_name.value")
    repo = CpmProductRepository(
        table_name=table_name,
        dynamodb_client=dynamodb_client(),
    )

    with pytest.raises(ItemNotFound):
        repo.read(product_team_id=product_team_id, product_id=product_id)


def test__cpm_product_repository_local():
    product_id = "P.XXX-YYY"

    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name"
    )
    cpm_product = product_team.create_cpm_product(
        name="cpm-product-name", product_id=product_id
    )

    with mock_table("my_table") as client:
        repo = CpmProductRepository(
            table_name="my_table",
            dynamodb_client=client,
        )

        repo.write(cpm_product)
        result = repo.read(
            product_team_id=product_team.id, product_id=cpm_product.id.id
        )
    assert result == cpm_product


def test__cpm_product_repository__product_does_not_exist_local():
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"

    with mock_table("my_table") as client:
        repo = CpmProductRepository(
            table_name="my_table",
            dynamodb_client=client,
        )
        with pytest.raises(ItemNotFound):
            repo.read(product_team_id=product_team_id, product_id=product_id)
