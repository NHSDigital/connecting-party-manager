import pytest
from domain.request_models import CreateDeviceReferenceDataIncomingParams
from pydantic import ValidationError

from test_helpers.sample_data import (
    CPM_DEVICE_REFERENCE_DATA,
    CPM_DEVICE_REFERENCE_DATA_EXTRA_PARAMS,
)


def test_device():
    product = CreateDeviceReferenceDataIncomingParams(**CPM_DEVICE_REFERENCE_DATA)
    assert isinstance(product, CreateDeviceReferenceDataIncomingParams)
    assert product.name == CPM_DEVICE_REFERENCE_DATA["name"]


def test_validate_cpm_product_raises_no_extra_fields():
    with pytest.raises(ValidationError) as exc:
        CreateDeviceReferenceDataIncomingParams(
            **CPM_DEVICE_REFERENCE_DATA_EXTRA_PARAMS
        )

    assert exc.value.model is CreateDeviceReferenceDataIncomingParams
