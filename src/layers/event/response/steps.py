from types import FunctionType


def render_response(data, cache) -> dict:
    return "OK"


response_steps: list[FunctionType] = [
    render_response,
]
