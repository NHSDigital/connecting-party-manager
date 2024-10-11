import pytest
from domain.core.cpm_product.v1 import CpmProduct
from domain.core.product_key.v1 import ProductKey, ProductKeyType
from domain.core.root.v3 import Root
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.errors import AlreadyExistsError

from test_helpers.uuid import consistent_uuid

PARTY_KEY = "ABC-123456"


@pytest.mark.integration
def test__product_repository__add_key(
    product: CpmProduct, repository: CpmProductRepository
):
    party_key = ProductKey(key_type=ProductKeyType.PARTY_KEY, key_value=PARTY_KEY)
    product.add_key(**party_key.dict())
    repository.write(product)

    product_by_id = repository.read(
        product_team_id=product.product_team_id, product_id=product.id
    )
    assert product_by_id.keys == [party_key]


@pytest.mark.integration
def test__product_repository__cannot_add_duplicate_key(
    product: CpmProduct, repository: CpmProductRepository
):
    """This test guards against Party Key clashes"""

    party_key = ProductKey(key_type=ProductKeyType.PARTY_KEY, key_value=PARTY_KEY)
    product.add_key(**party_key.dict())
    repository.write(product)

    # Create a second unrelated product
    org = Root.create_ods_organisation(ods_code="ABC")
    second_product_team = org.create_product_team(
        id=consistent_uuid(2), name="another-product-team-name"
    )
    second_product = second_product_team.create_cpm_product(
        name="another-cpm-product-name"
    )
    second_product.add_key(**party_key.dict())

    with pytest.raises(AlreadyExistsError):
        repository.write(second_product)
