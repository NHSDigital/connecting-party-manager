import os
from unittest import mock


def test_index():
    with mock.patch.dict(os.environ, {"SOMETHING": "hiya"}, clear=True):
        from api.status.index import handler

        result = handler(event={})
    assert result == {
        "statusCode": 200,
        "body": "OK",
        "headers": {"Content-Length": 2, "Content-Type": "application/json"},
    }
