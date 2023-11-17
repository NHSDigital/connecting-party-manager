import json
import os
from unittest import mock

import pytest
from hypothesis import given
from hypothesis.strategies import builds

from .model import ReadProductTeamEvent


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
@given(read_event=builds(ReadProductTeamEvent))
def test_index(read_event: ReadProductTeamEvent, version):
    with mock.patch.dict(os.environ, {"DYNAMODB_TABLE": "hiya"}, clear=True):
        from api.readProductTeam.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                **read_event.dict(),
            }
        )

    expected_result = json.dumps(f"ProductTeam({read_event.pathParameters.id})")

    assert result == {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": len(expected_result),
            "Content-Type": "application/json",
        },
    }
