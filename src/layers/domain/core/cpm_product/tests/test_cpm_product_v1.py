from datetime import datetime
from uuid import UUID

import pytest
from domain.core.cpm_product import CpmProduct
from domain.core.cpm_system_id.v1 import ProductId


@pytest.fixture
def cpm_product():
    product = CpmProduct(
        name="Foo",
        ods_code="ABC123",
        product_team_id="18934119-5780-4d28-b9be-0e6dff3908ba",
    )
    return product


def test_cpm_product_created(cpm_product: CpmProduct):
    assert isinstance(cpm_product.created_on, datetime)
    assert isinstance(cpm_product.id, ProductId)
    assert isinstance(cpm_product.name, str)
    assert isinstance(cpm_product.ods_code, str)
    assert isinstance(cpm_product.product_team_id, UUID)
    assert isinstance(cpm_product.created_on, datetime)


@pytest.mark.parametrize(
    "invalid_product_id",
    [
        "P.111-XXX",  # Contains invalid characters
        "P.AAA.AAA",  # Uses '.' instead of '-' as the separator
        "P.AC-33A",  # Not enough charactors
        "P.ACCC-33A",  # Too many charactors
    ],
)
def test_invalid_product_id(invalid_product_id):
    with pytest.raises(ValueError):
        CpmProduct(
            id=invalid_product_id,
            name="Foo",
            ods_code="ABC123",
            product_team_id="18934119-5780-4d28-b9be-0e6dff3908ba",
        )
