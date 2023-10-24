from uuid import UUID

import parse
from behave import register_type


@parse.with_pattern(
    r"\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}"
)
def parse_uuid(value):
    return UUID(value)


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
    UUID=parse_uuid,
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

    def inner(context, *args, **kwargs):
        try:
            func(context, *args, **kwargs)
        except Exception as e:
            context.error = e

    return inner


def assert_type_matches(obj, expected):
    actual = type(obj).__name__
    assert actual == expected, "Type mismatch: expected {expected} got {actual}"


def parse_value(v):
    """
    Use the parsing methods above to turn a value into a proper type.
    """

    def __parse_value(v, *funcs):
        [head, *tail] = funcs
        try:
            return head(v)
        except:
            return __parse_value(v, *tail)

    return __parse_value(v, parse_uuid, parse_number, parse_ods_code, parse_string)


def read_value_from_path(obj, path) -> any:
    def _read_value(obj, path) -> any:
        [head, *tail] = path
        obj = obj.__dict__[head]
        if len(tail) > 0:
            return _read_value(obj, tail)
        return obj

    return _read_value(obj, path.split("."))
