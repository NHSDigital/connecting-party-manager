from datetime import datetime
from uuid import UUID

import pytest
from domain.core.cpm_system_id import ProductId
from domain.core.enum import Environment
from domain.core.epr_product import EprProduct


@pytest.fixture
def epr_product():
    product = EprProduct(
        name="Foo",
        ods_code="ABC123",
        product_team_id="ABC123.18934119-5780-4d28-b9be-0e6dff3908ba",
    )
    return product


def test_epr_product_created(epr_product: EprProduct):
    assert isinstance(epr_product.created_on, datetime)
    assert isinstance(epr_product.id, ProductId)
    assert isinstance(epr_product.name, str)
    assert isinstance(epr_product.ods_code, str)
    assert isinstance(epr_product.product_team_id, str)
    assert isinstance(epr_product.created_on, datetime)


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
        EprProduct(
            id=invalid_product_id,
            name="Foo",
            ods_code="ABC123",
            product_team_id="ABC123.18934119-5780-4d28-b9be-0e6dff3908ba",
        )


def test_epr_product_create_device_reference_data(epr_product: EprProduct):
    device_reference_data = epr_product.create_device_reference_data(
        name="foo", environment=Environment.DEV
    )
    assert isinstance(device_reference_data.id, UUID)
    assert device_reference_data.name == "foo"
    assert device_reference_data.product_id == epr_product.id
    assert device_reference_data.product_team_id == epr_product.product_team_id
    assert device_reference_data.ods_code == epr_product.ods_code


def test_epr_product_create_device(epr_product: EprProduct):
    device = epr_product.create_device(name="foo", environment=Environment.DEV)
    assert isinstance(device.id, UUID)
    assert device.name == "foo"
    assert device.product_id == epr_product.id
    assert device.product_team_id == epr_product.product_team_id
    assert device.ods_code == epr_product.ods_code
