import pytest
from domain.core.cpm_product import CpmProduct
from domain.core.product_key import ProductKey, ProductKeyType
from domain.repository.cpm_product_repository import CpmProductRepository

KEY = "ABC123456"  # pragma: allowlist secret


@pytest.mark.integration
def test__product_repository__add_key(
    product: CpmProduct, repository: CpmProductRepository
):
    party_key = ProductKey(key_type=ProductKeyType.GENERAL, key_value=KEY)
    product.add_key(**party_key.dict())
    repository.write(product)
    product_by_id = repository.read(
        product_team_id=product.product_team_id, id=product.id
    )
    assert product_by_id.keys == [party_key]
