from domain.core.device_id import generate_device_key
from domain.core.validation import PRODUCT_ID_REGEX


def test__deterministic_generate():
    a = generate_device_key("product")
    b = generate_device_key("product")

    assert a != b
    assert PRODUCT_ID_REGEX.match(a) is not None
    assert PRODUCT_ID_REGEX.match(b) is not None
