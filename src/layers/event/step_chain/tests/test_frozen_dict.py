import pytest
from event.step_chain.types import FrozenDict


def test_frozen_dict():
    fd = FrozenDict(a=1, b=2)
    assert {**fd} == {"a": 1, "b": 2}
    assert fd["a"] == 1
    assert fd["b"] == 2


def test_frozen_dict_is_frozen():
    fd = FrozenDict(a=1, b=2)
    with pytest.raises(TypeError):
        fd["a"] = 3
