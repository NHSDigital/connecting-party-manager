import pytest
from domain.core.accredited_system_id import (
    AccreditedSystemId,
    InvalidAccreditedSystemIdError,
)


@pytest.mark.parametrize(
    "value",
    [
        "1",
        "999999999999",
    ],
)
def test__parse_value_success(value: str):
    actual = AccreditedSystemId(value)
    assert actual == value


@pytest.mark.parametrize(
    "value",
    [
        "-1",
        "1999999999999",
        "ONE MILLION",
    ],
)
def test__parse_value_invalid(value: str):
    with pytest.raises(InvalidAccreditedSystemIdError):
        AccreditedSystemId(value)
