from types import FunctionType

from event.response.render_response import render_response as _render_response
from event.step_chain import StepChain


def render_response(data, cache) -> dict:
    response = _render_response(response=data[StepChain.INIT])
    return response.dict()


response_steps: list[FunctionType] = [
    render_response,
]
