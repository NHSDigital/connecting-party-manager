from enum import Enum
from functools import wraps
from json import JSONDecodeError
from typing import Callable, ParamSpec, TypeVar

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from event.step_chain import StepChain
from pydantic import BaseModel, Extra, ValidationError

T = TypeVar("T")
RT = TypeVar("RT")
P = ParamSpec("P")


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


class InboundQueryValidationError(ValidationError):
    pass


def mark_json_decode_errors_as_inbound(function: Callable[P, RT]):
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


class DeviceType(str, Enum):
    PRODUCT = "PRODUCT"
    ENDPOINT = "ENDPOINT"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if value.upper() == member.value:
                return member


class SearchQueryParams(BaseModel, extra=Extra.forbid):
    device_type: DeviceType


def validate_query_params(function):
    @wraps(function)
    def decorator(data, cache, **kwargs):
        event = APIGatewayProxyEvent(data[StepChain.INIT])
        query_params = event.query_string_parameters
        try:
            SearchQueryParams(**query_params)
            return function(data, cache, **kwargs)
        except ValidationError as exc:
            raise InboundQueryValidationError(
                errors=exc.raw_errors,
                model=exc.model,
            )

    return decorator


def parse_validation_error(
    validation_error: ValidationError,
) -> list[ValidationErrorItem]:
    error_items = []
    inbound = False
    for error_item in validation_error.errors():
        if isinstance(validation_error, InboundValidationError):
            inbound = True
        if isinstance(validation_error, InboundQueryValidationError):
            error_item["msg"] = "Only 'device_type' query parameter is allowed."
            if error_item["type"] == "type_error.enum":
                error_item[
                    "msg"
                ] = "'device_type' query parameter must be one of 'product' or 'endpoint'."
            inbound = True
        error_items.append(error_item)

    return [
        ValidationErrorItem(
            model_name=validation_error.model.__name__,
            is_inbound=inbound,
            **error_item,
        )
        for error_item in error_items
    ]
