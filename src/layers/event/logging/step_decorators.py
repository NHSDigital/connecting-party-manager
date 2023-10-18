from types import FunctionType

from domain.response.error_collections import NonFatalErrorCollection
from nhs_context_logging import log_action as _log_action


def log_action(function):
    return _log_action(
        log_args=["data", "cache"],
        expected_errors=NonFatalErrorCollection,
        log_result=True,
    )(function)


logging_step_decorators: list[FunctionType] = [
    log_action,
]
