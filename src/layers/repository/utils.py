from typing import Any

from repository.errors import UnableToUnmarshall


def marshall_value(value):
    if value is None:
        return {"Null": True}
    if type(value) is bool:  # isinstance(True,int) == True
        return {"B": value}
    if type(value) is int or isinstance(value, float):
        return {"N": str(value)}
    if isinstance(value, list):
        return {"L": [marshall_value(item) for item in value]}
    if isinstance(value, dict):
        return {"M": {k: marshall_value(v) for (k, v) in value.items()}}
    return {"S": str(value)}


def marshall(d):
    return marshall_value(d)["M"]


def _unmarshall_mapping(mapping: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {k: unmarshall_value(v) for (k, v) in mapping["M"].items()}


def unmarshall_value(record: dict[str, Any]):
    if "Null" in record:
        return None
    if "S" in record:
        return str(record["S"])
    if "B" in record:
        return bool(record["B"])
    if "N" in record:
        return float(record["N"])
    if "S" in record:
        return str(record["S"])
    if "L" in record:
        return [unmarshall_value(v) for v in record["L"]]
    if "M" in record:
        return _unmarshall_mapping(mapping=record)
    raise UnableToUnmarshall(f"Unhandled record {record}")


def unmarshall(record) -> dict[str, Any]:
    return _unmarshall_mapping({"M": record})
