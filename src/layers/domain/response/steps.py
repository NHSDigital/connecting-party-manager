from types import FunctionType

from event.step_chain import StepChain

from .render_response import render_response as _render_response


def render_response(data, cache) -> dict:
    result, version, location = data[StepChain.INIT]
    response = _render_response(response=result, version=version, location=location)
    return response.dict()


response_steps: list[FunctionType] = [
    render_response,
]
