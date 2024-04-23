import json
from io import StringIO
from unittest.mock import Mock

import pytest
from etl_utils.trigger.notify import notify
from event.json import json_loads

from etl.notify.notify import handler

FUNCTION_NAME = "my-function"


def mocked_lambda(FunctionName, Payload):
    result = handler(event=json_loads(Payload))
    return {"Payload": StringIO(json.dumps(result))}


@pytest.mark.parametrize(
    ("input_result", "expected_result"),
    [
        ("all_good", "pass"),
        (ValueError("oops!"), "fail"),
    ],
)
def test_trigger_notify(input_result, expected_result):
    lambda_client = Mock()
    lambda_client.invoke.side_effect = mocked_lambda
    response = notify(
        lambda_client=lambda_client,
        function_name=FUNCTION_NAME,
        trigger_type="foo",
        result=input_result,
    )

    assert json_loads(response) == expected_result
