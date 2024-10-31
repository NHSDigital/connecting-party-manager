from dataclasses import asdict
from unittest import mock

from api.tests.feature_tests.steps.requests import make_request, mock_request

PATH = "api.tests.feature_tests.steps.requests.{}"


class Index:
    def __init__(self, response_body):
        self.response_body = response_body

    def handler(self, event):
        return {
            "statusCode": 200,
            "headers": {"Content-Length": len(self.response_body), "Version": "1"},
            "body": self.response_body,
        }


def test__mock_requests():
    response_body = "hiya"
    index = Index(response_body=response_body)

    with mock_request(), mock.patch(
        PATH.format("get_endpoint_lambda_mapping"),
        return_value={"GET": {"my_url/{id}/{something}/the_endpoint": index}},
    ):
        response = make_request(
            base_url="BASE_URL/my_url/my_id/my_something",
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
            "Host": None,
        },
        "status_code": 200,
        "reason": "OK",
        "url": "BASE_URL/my_url/my_id/my_something/the_endpoint",
    }
