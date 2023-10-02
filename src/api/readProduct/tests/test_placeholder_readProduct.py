import pytest
from domain.placeholder import placeholder

import api.readProduct.index  # noqa: F401


@pytest.mark.integration
def test_dummy_integration():
    placeholder()


def test_dummy_unit():
    placeholder()


@pytest.mark.smoke
def test_dummy_smoke():
    raise Exception("delete me")
