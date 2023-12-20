from dataclasses import asdict
from unittest import mock

from feature_tests.end_to_end.steps.requests import make_request, mock_request

PATH = "feature_tests.end_to_end.steps.requests.{}"


def test__mock_requests():
    response_body = "hiya"
    with mock_request(), mock.patch(
        PATH.format("get_endpoint_lambda_mapping"),
        return_value={
            "GET": {
                "my_url/{id}/{something}": lambda event: {
                    "statusCode": 200,
                    "headers": {"Content-Length": len(response_body), "Version": "1"},
                    "body": response_body,
                }
            }
        },
    ):
        response = make_request(
            base_url="my_url/my_id/my_something",
            http_method="GET",
            endpoint="/the_endpoint",
            body={"key": "value"},
            headers={"KEY": "VALUE"},
        )
    assert asdict(response) == {
        "text": response_body,
        "headers": {
            "Content-Length": str(len(response_body)),
            "Content-Type": "application/json",
            "Version": "1",
        },
        "status_code": 200,
        "reason": "OK",
        "url": "my_url/my_id/my_something/the_endpoint",
    }
