import parse
from behave import register_type
from domain.core.device import DeviceCreatedEvent, DeviceKeyAddedEvent
from domain.core.error import DuplicateError
from domain.core.product_team import ProductTeamCreatedEvent
from pydantic import ValidationError

from feature_tests.domain.steps.context import Context


def parse_string(value):
    return str(value)


@parse.with_pattern(r"-?[0-9]+")
def parse_number(value):
    return int(value)


@parse.with_pattern(r"[0-9A-Z]{1,5}")
def parse_ods_code(value):
    return value


@parse.with_pattern(r"(a|an)")
def parse_a_or_an(value):
    return value


@parse.with_pattern(r"[a-z0-9_]+(\.[a-z0-9_]+)*")
def parse_path(value):
    return value


# Register the different datatypes used in the step definitions.
register_type(
    String=parse_string,
    Number=parse_number,
    OdsCode=parse_ods_code,
    An=parse_a_or_an,
    Path=parse_path,
)


def catch_errors(func):
    """
    Decorator that will catch an exception and record it on the context
    """

    def inner(context: Context, *args, **kwargs):
        try:
            func(context=context, *args, **kwargs)
        except Exception as e:
            context.error = e

    return inner


EXPECTED_TYPES = {
    "ProductTeamCreatedEvent": ProductTeamCreatedEvent,
    "DeviceCreatedEvent": DeviceCreatedEvent,
    "DeviceKeyAddedEvent": DeviceKeyAddedEvent,
    "ValidationError": ValidationError,
    "DuplicateError": DuplicateError,
}


def assert_type_matches(obj, expected_type_name: str):
    expected_type = EXPECTED_TYPES.get(expected_type_name)
    if expected_type is None:
        raise ValueError(
            f"Type '{expected_type_name}' not registered in feature_tests.steps.common.EXPECTED_TYPES. "
            f"The actual type is '{type(obj).__name__}' - did you mean to register this?"
        )

    if type(obj) is not expected_type and isinstance(obj, Exception):
        raise obj

    assert (
        type(obj) is expected_type
    ), f"Type mismatch: expected {expected_type} got {type(obj)}"


def parse_value(v):
    """
    Use the parsing methods above to turn a value into a proper type.
    """
    _parsing_functions = (parse_number, parse_ods_code, parse_string)

    def __parse_value(v, *functions):
        if len(functions) == 0:
            raise ValueError(
                f"Could not parse '{v}' with any of {(f.__name__ for f in _parsing_functions)}"
            )

        head, *tail = functions
        try:
            return head(v)
        except:
            return __parse_value(v, *tail)

    return __parse_value(v, *_parsing_functions)


def read_value_from_path(obj, full_path: str) -> any:
    """
    Uses a json-like path to read a nested object attributes.
    """

    def _read_value(obj, path: list[str]) -> any:
        if not path:
            raise ValueError(
                f"Could not read a value at path {full_path} from object {obj}"
            )

        head, *tail = path
        head = head.replace("#DOT#", ".")
        if isinstance(obj, dict):
            obj = obj[head]
        else:
            obj = getattr(obj, head)
        if tail:
            return _read_value(obj, tail)
        return obj

    # path = full_path.replace("#.", "DOT")
    return _read_value(obj, full_path.split("."))
