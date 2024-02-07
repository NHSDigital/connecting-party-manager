from domain.response.aws_lambda_response import AwsLambdaResponse
from hypothesis import given
from hypothesis.strategies import builds, none


@given(aws_lambda_response=builds(AwsLambdaResponse, headers=none()))
def test_aws_lambda_response(aws_lambda_response: AwsLambdaResponse):
    assert aws_lambda_response.dict() == {
        "statusCode": aws_lambda_response.statusCode.value,
        "body": aws_lambda_response.body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": f"{len(aws_lambda_response.body)}",
            "Location": None,
            "Version": "null",
        },
    }
