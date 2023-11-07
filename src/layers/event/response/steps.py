from http import HTTPStatus
from types import FunctionType

from event.response.model import Response
from event.step_chain import StepChain


def _render_response(response) -> Response:
    if isinstance(response, HTTPStatus):
        status_code = response
        body = status_code.phrase

    elif isinstance(response, Exception):
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        body = f"{response.__class__.__name__}: {str(response)}"

    else:
        status_code = HTTPStatus.OK
        body = response

    return Response(statusCode=status_code, body=body)


def render_response(data, cache) -> dict:
    response = _render_response(response=data[StepChain.INIT])
    return response.dict()


response_steps: list[FunctionType] = [
    render_response,
]
