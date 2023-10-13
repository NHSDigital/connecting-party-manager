from functools import wraps
from types import FunctionType

from domain.response.error_collections import NonFatalErrorCollection
from nhs_context_logging import add_fields, log_action

from .log_reference import make_log_reference


def modify_logger(function):
    @wraps(function)
    def wrapper(data, cache):
        try:
            result = function(data=data, cache=cache)
        except Exception as exception:
            add_fields(result=exception)
            raise
        else:
            add_fields(result=result)
            return result

    return wrapper


def log_step(function):
    return log_action(
        action=f"{function.__module__}.{function.__name__}",
        log_reference=make_log_reference(name=function.__name__),
        log_args=["data", "cache"],
        expected_errors=NonFatalErrorCollection,
    )(function)


logging_step_decorators: list[FunctionType] = [log_step, modify_logger]
