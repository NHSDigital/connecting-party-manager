import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.errors import AlreadyExistsError, ItemNotFound

from test_helpers.uuid import consistent_uuid


@pytest.mark.integration
def test__cpm_product_repository(product: CpmProduct, repository: CpmProductRepository):
    repository.write(product)
    result = repository.read(
        product_team_id=product.product_team_id, product_id=product.id
    )
    assert result == product


@pytest.mark.integration
def test__cpm_product_repository_already_exists(
    product: CpmProduct, repository: CpmProductRepository
):
    repository.write(product)
    with pytest.raises(AlreadyExistsError):
        repository.write(product)


@pytest.mark.integration
def test__cpm_product_repository__product_does_not_exist(
    repository: CpmProductRepository,
):
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id=product_team_id, product_id=product_id)


def test__cpm_product_repository_local(
    product: CpmProduct, repository: CpmProductRepository
):
    repository.write(product)
    result = repository.read(
        product_team_id=product.product_team_id, product_id=product.id
    )
    assert result == product


def test__cpm_product_repository__product_does_not_exist_local(
    repository: CpmProductRepository,
):
    product_team_id = consistent_uuid(1)
    product_id = "P.XXX-YYY"
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id=product_team_id, product_id=product_id)
