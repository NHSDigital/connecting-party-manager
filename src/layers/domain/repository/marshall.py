from typing import Any

from .errors import UnableToUnmarshall

MARSHALL_FUNCTION_BY_TYPE = {
    type(None): (lambda _: {"NULL": True}),
    bool: (lambda x: {"BOOL": x}),
    int: (lambda x: {"N": str(x)}),
    float: (lambda x: {"N": str(x)}),
    list: (lambda x: {"L": [marshall_value(item) for item in x]}),
    tuple: (lambda x: {"L": [marshall_value(item) for item in x]}),
    dict: (lambda x: {"M": {k: marshall_value(v) for (k, v) in x.items()}}),
}


def marshall_value(value):
    fn = MARSHALL_FUNCTION_BY_TYPE.get(type(value), (lambda x: {"S": str(x)}))
    return fn(value)


def marshall(**data):
    return marshall_value(data)["M"]


def _unmarshall_mapping(mapping: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {k: unmarshall_value(v) for (k, v) in mapping["M"].items()}


def unmarshall_value(record: dict[str, str | dict | list]):
    ((_type_name, value),) = record.items()
    match _type_name:
        case "NULL":
            return None
        case "S":
            return str(value)
        case "BOOL":
            return bool(value)
        case "N":
            return int(value) if value.isdigit() else float(value)
        case "L":
            return list(map(unmarshall_value, value))
        case "M":
            return _unmarshall_mapping(mapping=record)
        case _:
            raise UnableToUnmarshall(f"Unhandled record {record}")


def unmarshall(record) -> dict[str, Any]:
    return _unmarshall_mapping({"M": record})
