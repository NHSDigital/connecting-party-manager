from event.response.aws_lambda_response import AwsLambdaResponse
from hypothesis import given
from hypothesis.strategies import builds, none


@given(aws_lambda_response=builds(AwsLambdaResponse, headers=none()))
def test_aws_lambda_response(aws_lambda_response: AwsLambdaResponse):
    aws_lambda_response.dict() == {
        "statusCode": aws_lambda_response.statusCode.value,
        "body": aws_lambda_response.body,
        "headers": {
            "content-type": "application/json",
            "content_length": len(aws_lambda_response.body),
        },
    }
