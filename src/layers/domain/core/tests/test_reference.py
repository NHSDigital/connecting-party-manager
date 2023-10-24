import pytest
from domain.core.reference import Reference


@pytest.mark.parametrize(
    "system,value,name_a,name_b",
    [["foo", "123", "Same Name", "Same Name"], ["bah", "456", "Name A", "Name B"]],
)
def test__equality(system: str, value: str, name_a: str, name_b: str):
    a = Reference(system, value, name_a)
    b = Reference(system, value, name_b)

    assert a == b, "Equals"


@pytest.mark.parametrize(
    "system_a,value_a,system_b,value_b",
    [
        ["a", "aa", "b", "bb"],
        ["same", "a", "same", "b"],
        ["a", "same", "b", "same"],
    ],
)
def test__inequality(system_a: str, value_a: str, system_b: str, value_b: str):
    a = Reference(system_a, value_a, "Same Name")
    b = Reference(system_b, value_b, "Same Name")

    assert a != b, "Not Equal"
