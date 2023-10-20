import os
from unittest import mock

import pytest


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    with mock.patch.dict(os.environ, {"SOMETHING": "hiya"}, clear=True):
        from api.createProduct.index import handler

        result = handler(event={"headers": {"version": version}})
    assert result == "OK"
