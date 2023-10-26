from types import FunctionType


def render_response(data, cache) -> dict:
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Content-Length": 123},
        "body": "OK",
    }


response_steps: list[FunctionType] = [
    render_response,
]
