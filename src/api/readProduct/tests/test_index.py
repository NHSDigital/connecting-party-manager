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
        from api.readProduct.index import handler

        result = handler(event={"headers": {"version": version}})
    assert result == {
        "statusCode": 200,
        "body": "OK",
        "headers": {"Content-Length": 123, "Content-Type": "application/json"},
    }
