import json
from http import HTTPStatus

from domain.response.error_response import ErrorResponse
from domain.response.response_matrix import http_status_from_exception
from nhs_context_logging import app_logger
from pydantic import ValidationError

from .aws_lambda_response import AwsLambdaResponse
from .validators import (
    validate_exception,
    validate_http_status_response,
    validate_json_serialisable_response,
)


def render_response[
    JsonSerialisable
](
    response: JsonSerialisable | HTTPStatus | Exception,
    id: str = None,  # Deprecated: remove when FHIR is removed
    version: str = None,
    location: str = None,
) -> AwsLambdaResponse:
    if id is None:
        id = app_logger.service_name

    if isinstance(response, HTTPStatus):
        # Convert response to an Exception if it is an invalid http status
        response = validate_http_status_response(response)
    elif not isinstance(response, (HTTPStatus, Exception)):
        # Convert response to an Exception if it isn't JSON serialisable
        response = validate_json_serialisable_response(response)

    if isinstance(response, Exception):
        response = validate_exception(response)

    if response == HTTPStatus.NO_CONTENT:
        http_status = response
        outcome = None
    elif isinstance(response, ValidationError):
        # Implicit failure from ValidationError
        outcome = ErrorResponse.from_validation_error(exception=response).dict()
        http_status = http_status_from_exception(exception=response)
    elif isinstance(response, Exception):
        # Implicit failure from all other Exceptions
        outcome = ErrorResponse.from_exception(exception=response).dict()
        http_status = http_status_from_exception(exception=response)
    elif isinstance(response, tuple):
        http_status, outcome = response
    else:
        # Implicit success (e.g. SEARCH, READ operations)
        http_status = HTTPStatus.OK
        outcome = response

    body = json.dumps(outcome) if outcome is not None else ""
    return AwsLambdaResponse(
        statusCode=http_status, body=body, version=version, location=location
    )
