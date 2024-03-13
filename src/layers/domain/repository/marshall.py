from typing import Any

from .errors import UnableToUnmarshall


def marshall_value(value):
    if value is None:
        return {"Null": True}
    if type(value) is bool:
        return {"BOOL": value}
    if type(value) is int or isinstance(value, float):
        return {"N": str(value)}
    if isinstance(value, list):
        return {"L": [marshall_value(item) for item in value]}
    if isinstance(value, dict):
        return {"M": {k: marshall_value(v) for (k, v) in value.items()}}
    return {"S": str(value)}


def marshall(
    pk,
    sk=None,
    pk_1=None,
    sk_1=None,
    pk_2=None,
    sk_2=None,
    pk_3=None,
    sk_3=None,
    pk_4=None,
    sk_4=None,
    pk_5=None,
    sk_5=None,
    **data,
):
    keys = {
        "pk": pk,
        "sk": sk,
        "pk_1": pk_1,
        "sk_1": sk_1,
        "pk_2": pk_2,
        "sk_2": sk_2,
        "pk_3": pk_3,
        "sk_3": sk_3,
        "pk_4": pk_4,
        "sk_4": sk_4,
        "pk_5": pk_5,
        "sk_5": sk_5,
    }
    non_null_keys = {k: v for k, v in keys.items() if v is not None}
    return _marshall({**non_null_keys, **data})


def _marshall(d):
    return marshall_value(d)["M"]


def _unmarshall_mapping(mapping: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {k: unmarshall_value(v) for (k, v) in mapping["M"].items()}


def unmarshall_value(record: dict[str, str | dict | list]):
    ((_type_name, value),) = record.items()
    match _type_name:
        case "Null":
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
