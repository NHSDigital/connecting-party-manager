import pytest


@pytest.mark.integration
def test_dummy_integration():
    raise Exception("delete me")


def test_dummy_unit():
    raise Exception("delete me")


@pytest.mark.smoke
def test_dummy_smoke():
    raise Exception("delete me")
