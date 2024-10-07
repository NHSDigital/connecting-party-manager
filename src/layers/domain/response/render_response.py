import json
from http import HTTPStatus

from nhs_context_logging import app_logger

from .aws_lambda_response import AwsLambdaResponse
from .operation_outcome import operation_outcome_not_ok, operation_outcome_ok
from .validators import (
    validate_exception,
    validate_http_status_response,
    validate_json_serialisable_response,
)


def render_response[
    JsonSerialisable
](
    response: JsonSerialisable | HTTPStatus | Exception,
    id: str = None,
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
    elif isinstance(response, HTTPStatus):
        # Explicit success (e.g. CREATE, DELETE, UPDATE operations)
        http_status = response
        outcome = operation_outcome_ok(id=id, http_status=http_status)
    elif isinstance(response, Exception):
        # Implicit failure
        http_status, outcome = operation_outcome_not_ok(id=id, exception=response)
    else:
        # Implicit success (e.g. SEARCH, READ operations)
        http_status = HTTPStatus.OK
        outcome = response

    body = json.dumps(outcome) if outcome is not None else ""
    return AwsLambdaResponse(
        statusCode=http_status, body=body, version=version, location=location
    )
