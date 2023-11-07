import json
import os
from unittest import mock

import pytest

from .data import product_team


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    with mock.patch.dict(os.environ, {"SOMETHING": "hiya"}, clear=True):
        from api.createProductTeam.index import handler

        result = handler(
            event={"headers": {"version": version}, "body": json.dumps(product_team)}
        )
    assert result == {
        "statusCode": 201,
        "body": "Created",
        "headers": {"Content-Length": 7, "Content-Type": "application/json"},
    }
