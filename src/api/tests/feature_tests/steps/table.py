import re
from typing import Any, TypeVar

from behave.model import Table

from test_helpers.uuid import consistent_uuid

FN_REGEX = re.compile(r"\${\s([a-zA-Z_]\w*)\(([^)]*)\)\s}")
EXPAND_FUNCTIONS = {
    "uuid": consistent_uuid,
    # behave formatter workarounds here:
    "dollar": lambda: "$",
    "pipe": lambda: "|",
}


def parse_table(table: Table) -> dict:
    key_heading, value_heading = table.headings
    _dict = {row[key_heading]: row[value_heading] for row in table.rows}
    return _unflatten_dict(_dict)


def _expand(value: str):
    _match: list[tuple[str, str]] = FN_REGEX.findall(value)
    for fn_name, _args in _match:
        args = filter(bool, map(str.strip, _args.split(",")))
        expanded_value = EXPAND_FUNCTIONS[fn_name](*args)
        value = FN_REGEX.sub(expanded_value, value)
    return value


T = TypeVar("T")


def _make_nested_dict(path: tuple[str], value: T) -> dict[str, T]:
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


def _unpack_nested_lists(obj: Any | dict[str, any]):
    """Recursively convert any dict to a list where all keys are integer-like"""
    if not isinstance(obj, dict) or not obj:
        return _expand(obj)
    if all(key.isdigit() for key in obj):
        unpacked_list = [None] * (int(max(obj)) + 1)
        for key, value in obj.items():
            unpacked_list[int(key)] = _unpack_nested_lists(value)
        return unpacked_list
    return {key: _unpack_nested_lists(value) for key, value in obj.items()}


def _unflatten_dict(flat_dict: dict[str, any]):
    nested_dict = {}
    for key, value in flat_dict.items():
        head, *tail = key.split(".")
        _nested_dict = _make_nested_dict(path=tail, value=value)

        if head not in nested_dict:
            nested_dict[head] = _nested_dict
        else:
            _merge_nested_dicts(nested_dict[head], _nested_dict)

    return _unpack_nested_lists(obj=nested_dict)
