import pytest
from domain.core.device_key.v2 import DeviceKeyType, validate_key
from domain.core.error import InvalidDeviceKeyError

GOOD_ID_EXAMPLES = {
    "product_id": "P.XXX-YYY",
    "accredited_system_id": "ABC:12345",
    "message_handling_system_id": "ABC:ABC-12345:abc123",
}


@pytest.mark.parametrize(["type", "key"], GOOD_ID_EXAMPLES.items())
def test_validate_key_pass(key, type):
    assert validate_key(key_value=key, key_type=DeviceKeyType(type)) == key


@pytest.mark.parametrize("type", GOOD_ID_EXAMPLES.keys())
@pytest.mark.parametrize("key", GOOD_ID_EXAMPLES.values())
def test_validate_key_fail(key, type):
    if (type, key) in GOOD_ID_EXAMPLES.items():
        pytest.skip("Already covered in 'test_validate_key_pass'")

    with pytest.raises(InvalidDeviceKeyError):
        validate_key(key_value=key, key_type=DeviceKeyType(type))


@pytest.mark.parametrize("type", GOOD_ID_EXAMPLES.keys())
@pytest.mark.parametrize(
    "key",
    (
        "12345",
        "ABC-12345",
        "XXX-YYY",
    ),
)
def test_validate_key_fail_other(key, type):
    with pytest.raises(InvalidDeviceKeyError):
        validate_key(key_value=key, key_type=DeviceKeyType(type))
