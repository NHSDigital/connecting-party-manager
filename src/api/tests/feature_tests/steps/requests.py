import json as _json
from contextlib import contextmanager
from dataclasses import dataclass
from unittest import mock
from urllib.parse import parse_qs, quote_plus

from aws_lambda_powertools.utilities.parser.models import APIGatewayProxyEventModel
from domain.response.aws_lambda_response import AwsLambdaResponse
from event.json import json_loads
from requests import HTTPError, Response, request

from api.tests.feature_tests.steps.data import DUMMY_CONTEXT
from api.tests.feature_tests.steps.endpoint_lambda_mapping import (
    get_endpoint_lambda_mapping,
    parse_api_path,
)

THIS_MODULE = "api.tests.feature_tests.steps.requests"


def _parse_url(base_url: str, endpoint: str) -> str:
    _endpoint, *tail = endpoint.split("?")
    query_string_parts = parse_qs(tail[0]) if tail else {}

    url = f"{base_url}{_endpoint}"
    query_params = [
        f"{quote_plus(query_param)}={quote_plus(value)}"
        for query_param, values in query_string_parts.items()
        for value in values
    ]
    if query_params:
        url += "?" + "&".join(query_params)

    return url


def make_request(
    base_url: str,
    http_method: str,
    endpoint: str,
    headers: dict[str, str],
    body: dict = None,
    raise_for_status=False,
) -> Response:
    url = _parse_url(base_url=base_url, endpoint=endpoint)
    json = body if type(body) is dict else None
    data = None if type(body) is dict else body
    response = request(
        method=http_method, url=url, headers=headers, json=json, data=data
    )
    if raise_for_status:
        try:
            response.raise_for_status()
        except HTTPError:
            print(response.text)  # noqa: T201
            raise
    return response


@dataclass
class MockedResponse:
    """A slimmed down version of 'requests.Response' for our purposes"""

    url: str
    text: str
    headers: dict[str, str]
    status_code: int
    reason: str

    def json(self):
        return json_loads(self.text)

    def raise_for_status(self):
        return Response.raise_for_status(self)


def _mocked_request(
    method: str,
    url: str,
    headers: dict[str, str],
    json: dict = None,
    data: str = None,
):
    """Implement the desired mocked behaviour of the 'request' function"""
    endpoint_lambda_mapping = get_endpoint_lambda_mapping()
    _, path = url.split(sep="/", maxsplit=1)
    path_params, query_params, index = parse_api_path(
        method=method,
        path=path,
        endpoint_lambda_mapping=endpoint_lambda_mapping,
    )
    optional_fields = {}
    if data:
        optional_fields["body"] = data
    if json:
        optional_fields["body"] = _json.dumps(json)
    if query_params:
        optional_fields["queryStringParameters"] = query_params
    if path_params:
        optional_fields["pathParameters"] = path_params
    event = APIGatewayProxyEventModel(
        resource=url,
        path=url,
        httpMethod=method,
        headers=headers,
        multiValueHeaders={"Host": ["foo.co.uk"]},
        requestContext=DUMMY_CONTEXT,
        isBase64Encoded=False,
        **optional_fields,
    )
    raw_response = index.handler(event.dict())
    response = AwsLambdaResponse(**raw_response)
    return MockedResponse(
        url=url,
        text=response.body,
        headers=response.headers.dict(),
        status_code=response.statusCode.value,
        reason=response.statusCode.phrase,
    )


@contextmanager
def mock_request():
    """
    This is to generally mock requests from the 'make_request' function.
    It is separated from the fixture below in order for to be unit-testable.
    """
    with mock.patch(f"{THIS_MODULE}.request", side_effect=_mocked_request):
        yield
