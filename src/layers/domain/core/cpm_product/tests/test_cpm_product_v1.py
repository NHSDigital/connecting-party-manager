from datetime import datetime
from uuid import UUID

import pytest
from domain.core.cpm_product import CpmProduct


@pytest.fixture
def cpm_product():
    return CpmProduct(
        id="P.BBB-AAA",
        name="Foo",
        ods_code="ABC123",
        product_team_id="18934119-5780-4d28-b9be-0e6dff3908ba",
    )


def test_cpm_product_created_with_datetime(cpm_product: CpmProduct):
    assert isinstance(cpm_product.created_on, datetime)


def test_device_created(cpm_product: CpmProduct):
    assert isinstance(cpm_product.id, str)
    assert isinstance(cpm_product.name, str)
    assert isinstance(cpm_product.ods_code, str)
    assert isinstance(cpm_product.product_team_id, UUID)
    assert isinstance(cpm_product.created_on, datetime)
