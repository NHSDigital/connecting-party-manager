import pytest
from domain.core.cpm_product import CpmProduct
from domain.core.product_key import ProductKey, ProductKeyType
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.errors import AlreadyExistsError, ItemNotFound

from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID

PARTY_KEY = "ABC-123456"


@pytest.mark.integration
def test__product_repository__add_key(
    product: CpmProduct, repository: CpmProductRepository
):
    party_key = ProductKey(key_type=ProductKeyType.PARTY_KEY, key_value=PARTY_KEY)
    product.add_key(**party_key.dict())
    repository.write(product)

    product_by_id = repository.read(
        product_team_id=product.product_team_id, id=product.id
    )
    assert product_by_id.keys == [party_key]


@pytest.mark.integration
def test__product_repository__add_key_then_delete(
    product: CpmProduct, repository: CpmProductRepository
):
    party_key = ProductKey(key_type=ProductKeyType.PARTY_KEY, key_value=PARTY_KEY)
    product.add_key(**party_key.dict())
    repository.write(product)

    product_from_db = repository.read(
        product_team_id=product.product_team_id, id=product.id
    )
    assert product_from_db.keys == [party_key]
    product_from_db.delete()
    repository.write(product_from_db)

    # No longer retrievable
    with pytest.raises(ItemNotFound):
        repository.read(product_team_id=product.product_team_id, id=product.id)


@pytest.mark.integration
def test__product_repository__cannot_add_duplicate_key(
    product: CpmProduct, repository: CpmProductRepository
):
    """This test guards against Party Key clashes"""

    party_key = ProductKey(key_type=ProductKeyType.PARTY_KEY, key_value=PARTY_KEY)
    product.add_key(**party_key.dict())
    repository.write(product)

    # Create a second unrelated product
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    second_product_team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )
    second_product = second_product_team.create_cpm_product(
        name="another-cpm-product-name"
    )
    second_product.add_key(**party_key.dict())

    with pytest.raises(AlreadyExistsError):
        repository.write(second_product)
