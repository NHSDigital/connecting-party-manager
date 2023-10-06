import pytest
from domain.core.entity import Entity


class TestEntityRed(Entity):
    __test__ = False


class TestEntityBlue(Entity):
    __test__ = False


@pytest.mark.parametrize("id,name", [["a", "A"], ["b", "B"]])
def test_entity_red_constructor(id: str, name: str):
    subject = TestEntityRed(id, name)

    assert subject.id == id, "id"
    assert subject.name == name, "name"


@pytest.mark.parametrize("id,name", [["x", "X"], ["y", "Y"]])
def test_entity_blue_constructor(id: str, name: str):
    """
    Just want to confirm this behaviour as we rely on it in tests below
    """
    subject = TestEntityBlue(id, name)

    assert subject.id == id, "id"
    assert subject.name == name, "name"


def test_same_references_are_equal():
    a = TestEntityRed("id", "name")
    b = a

    assert a == b, "reference equality"


@pytest.mark.parametrize("id", ["1", "2", "3"])
def test_different_instances_are_equal(id: str):
    a = TestEntityRed(id, "name")
    b = TestEntityRed(id, "name")

    assert a == b, "Entity equality"


def test_same_class_different_id_are_not_equal():
    a = TestEntityRed("x", "name")
    b = TestEntityRed("y", "name")

    assert a != b, "Entity inequality by id"


def test_same_class_same_id_are_equal():
    a = TestEntityBlue("x", "name")
    b = TestEntityBlue("x", "name")

    assert a == b, "Entity equality by class"


@pytest.mark.parametrize("id", ["a", "b"])
def test_different_class_same_id_are_not_equal(id: str):
    a = TestEntityRed(id, "name")
    b = TestEntityBlue(id, "name")

    assert a.id == id
    assert b.id == id
    assert a != b, "Class inequality"


def test_none_are_equal():
    a = TestEntityBlue(None, "name")
    b = TestEntityBlue(None, "none")

    assert a == b, "None"


@pytest.mark.parametrize("id", ["alpha", "beta", "gamma"])
def test_hashing_is_based_on_id(id: str):
    a = TestEntityRed(id, "name")
    b = TestEntityBlue(id, "name")

    assert hash(a) == hash(b), "hash"
