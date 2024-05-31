from enum import auto

import pytest
from sds.domain.constants import CaseInsensitiveEnum


def test_CaseInsensitiveEnum():
    class MyType(CaseInsensitiveEnum):
        FOO = auto()
        BAR = auto()

    assert MyType("FOO") == MyType.FOO
    assert MyType("foO") == MyType.FOO
    assert MyType("foo") == MyType.FOO


def test_CaseInsensitiveEnum_not_a_string():
    class MyType(CaseInsensitiveEnum):
        ...

    with pytest.raises(ValueError) as error:
        MyType(123)

    assert (
        str(error.value)
        == "123 is not a valid test_CaseInsensitiveEnum_not_a_string.<locals>.MyType"
    )
