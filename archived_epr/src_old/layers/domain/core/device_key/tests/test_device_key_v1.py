import pytest
from domain.core.device_key import DeviceKeyType, validate_key
from domain.core.error import InvalidKeyPattern

GOOD_ID_EXAMPLES = {
    "product_id": "P.XXX-YYY",
    "accredited_system_id": "12345",
    "cpa_id": "asdefe",
}


@pytest.mark.parametrize(["type", "key"], GOOD_ID_EXAMPLES.items())
def test_validate_key_pass(key, type):
    assert validate_key(key_value=key, key_type=DeviceKeyType(type)) == key


def test_validate_key_fail_other():
    with pytest.raises(InvalidKeyPattern):
        validate_key(key_value="aefaer", key_type=DeviceKeyType("product_id"))
