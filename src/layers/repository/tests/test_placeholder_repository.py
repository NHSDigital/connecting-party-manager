import pytest
from repository.placeholder import placeholder


@pytest.mark.integration
def test_dummy_integration():
    placeholder()


def test_dummy_unit():
    placeholder()


@pytest.mark.smoke
def test_dummy_smoke():
    raise Exception("delete me")