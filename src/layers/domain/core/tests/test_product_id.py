from domain.core.device_id import generate_device_key
from domain.core.device_key import DeviceKeyType
from domain.core.validation import CpmId


def test__deterministic_generate():
    a = generate_device_key(DeviceKeyType.PRODUCT_ID)
    b = generate_device_key(DeviceKeyType.PRODUCT_ID)

    assert a != b
    assert CpmId.Product.ID_PATTERN.match(a) is not None
    assert CpmId.Product.ID_PATTERN.match(b) is not None


def test__deterministic_generate_failure():
    a = "FOO"
    assert CpmId.Product.ID_PATTERN.match(a) is None
