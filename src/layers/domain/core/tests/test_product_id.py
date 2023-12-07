import pytest
from domain.core.product_id import PRODUCT_ID_REGEX, generate_product_id


@pytest.mark.parametrize("seed", [1, 2, 3])
def test__deterministic_generate(seed: int):
    a = generate_product_id(seed)
    b = generate_product_id(seed)

    assert a == b
    assert PRODUCT_ID_REGEX.match(a) is not None


def test__deterministic_generate_without_seed():
    a = generate_product_id()
    assert PRODUCT_ID_REGEX.match(a) is not None
