import json
from http import HTTPStatus

from domain.response.error_response import ErrorResponse
from domain.response.response_matrix import http_status_from_exception
from pydantic import ValidationError

from .aws_lambda_response import AwsLambdaResponse
from .validators import (
    validate_exception,
    validate_http_status_response,
    validate_json_serialisable_response,
)


def _exception_to_response_tuple(exception: Exception) -> tuple[HTTPStatus, object]:
    _exception = validate_exception(exception)
    exception_renderer = (
        ErrorResponse.from_validation_error
        if isinstance(exception, ValidationError)
        else ErrorResponse.from_exception
    )
    outcome = exception_renderer(exception=_exception).dict()
    http_status = http_status_from_exception(exception=_exception)
    return http_status, outcome


def render_response(
    response: Exception | tuple[HTTPStatus, object], version: str = None
) -> AwsLambdaResponse:
    if isinstance(response, Exception):
        http_status, outcome = _exception_to_response_tuple(exception=response)
    else:
        http_status, outcome = response
        try:
            validate_http_status_response(http_status=http_status)
            validate_json_serialisable_response(item=outcome)
        except Exception as exception:
            http_status, outcome = _exception_to_response_tuple(exception=exception)

    body = json.dumps(outcome) if outcome is not None else ""
    return AwsLambdaResponse(statusCode=http_status, body=body, version=version)
