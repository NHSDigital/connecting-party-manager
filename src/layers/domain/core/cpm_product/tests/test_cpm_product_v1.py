from datetime import datetime
from uuid import UUID

import pytest
from domain.core.cpm_product import CpmProduct
from domain.core.cpm_system_id import ProductId


@pytest.fixture
def cpm_product():
    product = CpmProduct(
        name="Foo",
        ods_code="ABC123",
        product_team_id="ABC123.18934119-5780-4d28-b9be-0e6dff3908ba",
    )
    return product


def test_cpm_product_created(cpm_product: CpmProduct):
    assert isinstance(cpm_product.created_on, datetime)
    assert isinstance(cpm_product.id, ProductId)
    assert isinstance(cpm_product.name, str)
    assert isinstance(cpm_product.ods_code, str)
    assert isinstance(cpm_product.product_team_id, str)
    assert isinstance(cpm_product.created_on, datetime)


@pytest.mark.parametrize(
    "invalid_product_id",
    [
        "P.111-XXX",  # Contains invalid characters
        "P.AAA.AAA",  # Uses '.' instead of '-' as the separator
        "P.AC-33A",  # Not enough characters
        "P.ACCC-33A",  # Too many characters
    ],
)
def test_invalid_product_id(invalid_product_id):
    with pytest.raises(ValueError):
        CpmProduct(
            id=invalid_product_id,
            name="Foo",
            ods_code="ABC123",
            product_team_id="ABC123.18934119-5780-4d28-b9be-0e6dff3908ba",
        )


def test_cpm_product_create_device_reference_data(cpm_product: CpmProduct):
    device_reference_data = cpm_product.create_device_reference_data(name="foo")
    assert isinstance(device_reference_data.id, UUID)
    assert device_reference_data.name == "foo"
    assert device_reference_data.product_id == cpm_product.id
    assert device_reference_data.product_team_id == cpm_product.product_team_id
    assert device_reference_data.ods_code == cpm_product.ods_code


def test_cpm_product_create_device(cpm_product: CpmProduct):
    device = cpm_product.create_device(name="foo")
    assert isinstance(device.id, UUID)
    assert device.name == "foo"
    assert device.product_id == cpm_product.id
    assert device.product_team_id == cpm_product.product_team_id
    assert device.ods_code == cpm_product.ods_code
