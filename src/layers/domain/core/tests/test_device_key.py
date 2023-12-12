import pytest
from domain.core.device_key import DeviceKeyType, validate_key
from domain.core.error import InvalidDeviceKeyError


@pytest.mark.parametrize(
    ["type", "key"],
    (
        ("product_id", "XXX-YYY"),
        ("accredited_system_id", "12345"),
    ),
)
def test_validate_key_pass(key, type):
    assert validate_key(key=key, type=DeviceKeyType(type)) == key


@pytest.mark.parametrize(
    ["type", "key"],
    (
        ("product_id", "12345"),
        ("accredited_system_id", "XXX-YYY"),
    ),
)
def test_validate_key_fail(key, type):
    with pytest.raises(InvalidDeviceKeyError):
        assert validate_key(key=key, type=DeviceKeyType(type)) == key
