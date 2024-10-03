import pytest
from domain.core.error import NotFoundError
from domain.core.root.v3 import Root
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.errors import ItemNotFound
from event.aws.client import dynamodb_client

from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output
from test_helpers.uuid import consistent_uuid


@pytest.mark.integration
def test__cpm_product_repository_delete():
    repo = CpmProductRepository(
        table_name=read_terraform_output("dynamodb_table_name.value"),
        dynamodb_client=dynamodb_client(),
    )

    # Create product
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name"
    )
    cpm_product = product_team.create_cpm_product(name="cpm-product-name")
    repo.write(cpm_product)

    # Read and delete product
    product_from_db = repo.read(
        product_team_id=product_team.id, product_id=cpm_product.id.id
    )
    product_from_db.delete()
    repo.write(product_from_db)

    # No longer retrievable
    with pytest.raises(ItemNotFound):
        repo.read(product_team_id=product_team.id, product_id=cpm_product.id.id)


@pytest.mark.integration
def test__cpm_product_repository_cannot_delete_if_does_not_exist():
    repo = CpmProductRepository(
        table_name=read_terraform_output("dynamodb_table_name.value"),
        dynamodb_client=dynamodb_client(),
    )

    # Create product with no events (should be impossible)
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name"
    )
    cpm_product = product_team.create_cpm_product(name="cpm-product-name")
    cpm_product.clear_events()

    # Cannot delete the product, since doesn't exist
    cpm_product.delete()

    with pytest.raises(NotFoundError):
        repo.write(cpm_product)


def test__cpm_product_repository_delete_local():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name"
    )
    cpm_product = product_team.create_cpm_product(name="cpm-product-name")

    with mock_table("my-table") as client:
        repo = CpmProductRepository(table_name="my-table", dynamodb_client=client)

        # Create product
        repo.write(cpm_product)

        # Read and delete product
        product_from_db = repo.read(
            product_team_id=product_team.id, product_id=cpm_product.id.id
        )
        product_from_db.delete()
        repo.write(product_from_db)

        # No longer retrievable
        with pytest.raises(ItemNotFound):
            repo.read(product_team_id=product_team.id, product_id=cpm_product.id.id)


def test__cpm_product_repository_cannot_delete_if_does_not_exist_local():
    # Create product with no events (should be impossible)
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name"
    )
    cpm_product = product_team.create_cpm_product(name="cpm-product-name")
    cpm_product.clear_events()

    with mock_table("my-table") as client:
        repo = CpmProductRepository(table_name="my-table", dynamodb_client=client)

        # Cannot delete the product, since doesn't exist
        cpm_product.delete()
        with pytest.raises(NotFoundError):
            repo.write(cpm_product)
