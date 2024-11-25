import pytest
from domain.request_models import CreateCpmProductIncomingParams
from pydantic import ValidationError

from test_helpers.sample_data import CPM_PRODUCT, CPM_PRODUCT_EXTRA_PARAMS


def test_cpm_product():
    product = CreateCpmProductIncomingParams(**CPM_PRODUCT)
    assert isinstance(product, CreateCpmProductIncomingParams)
    assert product.name == CPM_PRODUCT["name"]


def test_validate_cpm_product_raises_no_extra_fields():
    with pytest.raises(ValidationError) as exc:
        CreateCpmProductIncomingParams(**CPM_PRODUCT_EXTRA_PARAMS)

    assert exc.value.model is CreateCpmProductIncomingParams
