import re
from typing import Any

from behave.model import Table

from api.tests.feature_tests.steps.context import Context
from test_helpers.uuid import consistent_uuid

FN_REGEX = re.compile(r"\${\s([a-zA-Z_]\w*)\(([^)]*)\)\s}")
JSON_PATH_PATTERN = re.compile(r"\.([^\.\[\]]+|\d+)")
EMPTY_TYPES_AS_STRING = {
    "[]": list,
    "{}": dict,
}

NUMERIC_FN_REGEX = re.compile(r"\${\sinteger\(([^)]*)\)\s}")


EXPAND_FUNCTIONS = {
    # macros here
    "uuid": lambda *args, **kwargs: consistent_uuid(*args),
    "note": lambda alias, context: context.notes[alias],
    # behave formatter workarounds here:
    "dollar": lambda context: "$",
    "pipe": lambda context: "|",
}


def _split_jsonpath(jsonpath: str):
    if not jsonpath.startswith("$."):
        return None
    segments: list[str] = JSON_PATH_PATTERN.findall(jsonpath)
    return [int(item) if item.isdigit() else item for item in segments]


def extract_from_response_by_jsonpath(response: dict, jsonpath: str):
    _jsonpath_segments = _split_jsonpath(jsonpath=jsonpath)
    value = response
    for key in _jsonpath_segments:
        value = value[key]
    return value


def parse_table(context: Context, table: Table) -> dict:
    key_heading, value_heading = table.headings
    _dict = {row[key_heading]: row[value_heading] for row in table.rows}
    return _unflatten_dict(_dict, context=context)


def expand_macro(value: str, *, context: Context):
    if value in EMPTY_TYPES_AS_STRING:
        return EMPTY_TYPES_AS_STRING[value]()

    _numeric_match = NUMERIC_FN_REGEX.match(value)
    if _numeric_match:
        (_value,) = _numeric_match.groups()
        return int(_value)

    _match: list[tuple[str, str]] = FN_REGEX.findall(value)
    for fn_name, _args in _match:
        value_to_replace = f"${{ {fn_name}({_args}) }}"
        args = filter(bool, map(str.strip, _args.split(",")))
        expanded_value = EXPAND_FUNCTIONS[fn_name](*args, context=context)
        value = value.replace(value_to_replace, expanded_value)
    return value


def _make_nested_dict[T](path: tuple[str], value: T) -> dict[str, T]:
    """Recursively convert a path to a nested dict"""
    if path:
        head, *tail = path
        return {head: _make_nested_dict(path=tail, value=value)}
    else:
        return value


def _merge_nested_dicts(d1, d2):
    """Merge two nested dictionaries together"""
    for key in d2:
        if key in d1:
            if isinstance(d2[key], dict) and isinstance(d1[key], dict):
                _merge_nested_dicts(d1[key], d2[key])
        else:
            d1[key] = d2[key]

    return d1


def _unpack_nested_lists(obj: Any | dict[str, any], context: Context):
    """Recursively convert any dict to a list where all keys are integer-like"""
    if not isinstance(obj, dict) or not obj:
        return expand_macro(obj, context=context)

    if all(key.isdigit() for key in obj):
        unpacked_list = [None] * (int(max(obj)) + 1)
        for key, value in obj.items():
            unpacked_list[int(key)] = _unpack_nested_lists(value, context=context)
        return unpacked_list
    return {
        key: _unpack_nested_lists(value, context=context) for key, value in obj.items()
    }


def _unflatten_dict(flat_dict: dict[str, any], context: Context):
    nested_dict = {}
    for key, value in flat_dict.items():
        head, *tail = key.split(".")
        _nested_dict = _make_nested_dict(path=tail, value=value)

        if head not in nested_dict:
            nested_dict[head] = _nested_dict
        else:
            _merge_nested_dicts(nested_dict[head], _nested_dict)

    return _unpack_nested_lists(obj=nested_dict, context=context)
