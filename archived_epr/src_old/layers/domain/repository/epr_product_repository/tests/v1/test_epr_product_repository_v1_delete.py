import pytest
from domain.core.epr_product import EprProduct
from domain.core.error import NotFoundError
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.errors import ItemNotFound


@pytest.mark.integration
def test__epr_product_repository_delete(
    product: EprProduct, repository: EprProductRepository
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
def test__epr_product_repository_cannot_delete_if_does_not_exist(
    product: EprProduct, repository: EprProductRepository
):
    product.clear_events()
    product.delete()
    with pytest.raises(NotFoundError):
        repository.write(product)


def test__epr_product_repository_delete_local(
    product: EprProduct, repository: EprProductRepository
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


def test__epr_product_repository_cannot_delete_if_does_not_exist_local(
    product: EprProduct, repository: EprProductRepository
):
    product.clear_events()
    product.delete()
    with pytest.raises(NotFoundError):
        repository.write(product)
