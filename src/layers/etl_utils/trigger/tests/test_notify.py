import boto3
import pytest
from etl_utils.trigger.notify import notify
from event.json import json_loads
from moto import mock_aws

FUNCTION_NAME = "my-function"
ROLE_NAME = "my-role"


@pytest.mark.parametrize(
    ("input_result", "expected_status", "expected_error_message"),
    [
        ("all_good", "Successful", None),
        (ValueError("oops!"), "Unsuccessful", "oops!"),
    ],
)
def test_trigger_notify(input_result, expected_status, expected_error_message):
    with mock_aws(config={"lambda": {"use_docker": False}}):
        lambda_client = boto3.client("lambda", region_name="us-east-1")
        iam_client = boto3.client("iam", region_name="us-east-1")
        iam_response = iam_client.create_role(
            RoleName=ROLE_NAME, AssumeRolePolicyDocument="some policy"
        )
        lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime="python3.10",
            Role=iam_response["Role"]["Arn"],
            Handler="notify.handler",
            Code={"ZipFile": ""},
            Publish=True,
        )
        response = notify(
            lambda_client=lambda_client,
            function_name=FUNCTION_NAME,
            trigger_type="foo",
            result=input_result,
        )
        iam_client.delete_role(RoleName=ROLE_NAME)
        lambda_client.delete_function(FunctionName=FUNCTION_NAME)
    assert json_loads(response) == {
        "message": f"{expected_status} 'foo' trigger of state machine.",
        "error_message": expected_error_message,
    }
