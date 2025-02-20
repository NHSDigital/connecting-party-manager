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
    class MyType(CaseInsensitiveEnum): ...

    with pytest.raises(TypeError) as error:
        MyType(123)

    assert (
        str(error.value)
        == "<enum 'MyType'> has no members; specify `names=()` if you meant to create a new, empty, enum"
    )
