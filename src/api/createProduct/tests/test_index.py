import pytest

from api.createProduct.index import handler


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    result = handler(event={"headers": {"version": version}})
    assert result == "OK"
