from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from pydantic import ValidationError

T = TypeVar("T")
RT = TypeVar("RT")
P = ParamSpec("P")


class InboundValidationError(ValidationError):
    pass


def mark_validation_errors_as_inbound(function: Callable[P, RT]):
    @wraps(function)
    def decorator(*args: P.args, **kwargs: P.kwargs):
        try:
            return function(*args, **kwargs)
        except ValidationError as validation_error:
            raise InboundValidationError(
                errors=validation_error.raw_errors,
                model=validation_error.model,
            )

    return decorator


def _path_to_error(model_name: str, error: dict) -> str:
    return ".".join((model_name, *map(str, error["loc"])))


def get_path_error_mapping(validation_error: ValidationError) -> dict[str, str]:
    """Returns {path.to.field --> error_msg} mapping"""
    model_name = validation_error.model.__name__
    return {
        _path_to_error(model_name=model_name, error=error): error["msg"]
        for error in validation_error.errors()
    }
