import pytest
from domain.core.ods_code import InvalidOdsCodeError, OdsCode


@pytest.mark.parametrize(
    "value",
    [
        "X26",
        "AB123",
        "8JK09",
    ],
)
def test__parse_value_success(value: str):
    actual = OdsCode(value)
    assert actual == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "AB1234",
    ],
)
def test__parse_value_invalid(value: str):
    with pytest.raises(InvalidOdsCodeError):
        OdsCode(value)
