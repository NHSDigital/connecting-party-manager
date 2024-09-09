from functools import wraps
from json import JSONDecodeError
from typing import Callable

from pydantic import BaseModel, ValidationError


class ValidationErrorItem(BaseModel):
    model_name: str
    is_inbound: bool
    loc: tuple[str, ...]
    msg: str
    type: str

    @property
    def exception_type(self) -> type[Exception]:
        if self.is_inbound and self.type == "value_error.missing":
            return InboundMissingValue
        elif self.is_inbound:
            return InboundValidationError
        return ValidationError

    @property
    def path(self):
        return ".".join((self.model_name, *map(str, self.loc)))


class InboundValidationError(ValidationError):
    pass


class InboundMissingValue(ValidationError):
    pass


class InboundJSONDecodeError(JSONDecodeError):
    pass


def mark_json_decode_errors_as_inbound[RT, **P](function: Callable[P, RT]):
    @wraps(function)
    def decorator(*args: P.args, **kwargs: P.kwargs):
        try:
            return function(*args, **kwargs)
        except JSONDecodeError as json_decode_error:
            raise InboundJSONDecodeError(
                msg="Invalid JSON body was provided",
                doc=json_decode_error.doc,
                pos=json_decode_error.pos,
            )

    return decorator


def mark_validation_errors_as_inbound[RT, **P](function: Callable[P, RT]):
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


def parse_validation_error(
    validation_error: ValidationError,
) -> list[ValidationErrorItem]:
    return [
        ValidationErrorItem(
            model_name=validation_error.model.__name__,
            is_inbound=isinstance(validation_error, InboundValidationError),
            **error_item,
        )
        for error_item in validation_error.errors()
    ]
