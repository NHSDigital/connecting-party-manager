import pytest
from domain.request_models.v1 import CreateDeviceIncomingParams
from pydantic import ValidationError

from test_helpers.sample_data import CPM_DEVICE, CPM_DEVICE_EXTRA_PARAMS


def test_device():
    product = CreateDeviceIncomingParams(**CPM_DEVICE)
    assert isinstance(product, CreateDeviceIncomingParams)
    assert product.name == CPM_DEVICE["name"]


def test_validate_cpm_product_raises_no_extra_fields():
    with pytest.raises(ValidationError) as exc:
        CreateDeviceIncomingParams(**CPM_DEVICE_EXTRA_PARAMS)

    assert exc.value.model is CreateDeviceIncomingParams
