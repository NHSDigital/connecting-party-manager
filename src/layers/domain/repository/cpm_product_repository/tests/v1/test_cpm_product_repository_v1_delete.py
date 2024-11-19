import pytest
from domain.core.cpm_product import CpmProduct
from domain.core.error import NotFoundError
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.errors import ItemNotFound


@pytest.mark.integration
def test__cpm_product_repository_delete(
    product: CpmProduct, repository: CpmProductRepository
):
    repository.write(product)  # Create product in DB
    product_from_db = repository.read(
        product_team_id=product.product_team_id, id=product.id
    )
    product_from_db.delete()
    repository.write(product_from_db)

    # No longer retrievable
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id=product.product_team_id, id=product.id)


@pytest.mark.integration
def test__cpm_product_repository_cannot_delete_if_does_not_exist(
    product: CpmProduct, repository: CpmProductRepository
):
    product.clear_events()
    product.delete()
    with pytest.raises(NotFoundError):
        repository.write(product)


def test__cpm_product_repository_delete_local(
    product: CpmProduct, repository: CpmProductRepository
):
    repository.write(product)  # Create product in DB
    product_from_db = repository.read(
        product_team_id=product.product_team_id, id=product.id
    )
    product_from_db.delete()
    repository.write(product_from_db)

    # No longer retrievable
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id=product.product_team_id, id=product.id)


def test__cpm_product_repository_cannot_delete_if_does_not_exist_local(
    product: CpmProduct, repository: CpmProductRepository
):
    product.clear_events()
    product.delete()
    with pytest.raises(NotFoundError):
        repository.write(product)
