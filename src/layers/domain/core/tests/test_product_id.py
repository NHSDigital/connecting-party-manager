import pytest
from domain.core.product_id import InvalidProductIdError, ProductId


@pytest.mark.parametrize("value", ["XXX-XXX-XXX"])
def test__parse_value_success(value: str):
    actual = ProductId(value)
    assert actual == value


@pytest.mark.parametrize(
    "value",
    [
        "!!!-!!!-!!!",
        "XXX-XXX-XXX-XXX",
    ],
)
def test__parse_value_invalid(value: str):
    with pytest.raises(InvalidProductIdError):
        ProductId(value)


@pytest.mark.parametrize("seed", [1, 2, 3])
def test__deterministic_generate(seed: int):
    a = ProductId.generate(seed)
    b = ProductId.generate(seed)

    assert a == b


def test__deterministic_generate_without_seed():
    a = ProductId.generate()
    ProductId(a)  # expect no exception
