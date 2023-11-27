from enum import Enum

from repository.errors import UnableToUnmarshall


def marshall_value(value):
    if value is None:
        return {"Null": True}
    if isinstance(value, Enum):
        return {"S": str(value._value_)}
    if isinstance(value, bool):  # isinstance(True,int) == True
        return {"B": value}
    if isinstance(value, int) or isinstance(value, float):
        return {"N": value}
    if isinstance(value, list):
        return {"L": [marshall_value(item) for item in value]}
    if isinstance(value, dict):
        return {"M": {k: marshall_value(v) for (k, v) in value.items()}}
    return {"S": str(value)}


def marshall(d):
    return marshall_value(d)["M"]


def unmarshall_value(record: dict[str, any]):
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
        return {k: unmarshall_value(v) for (k, v) in record["M"].items()}
    raise UnableToUnmarshall(f"Unhandled record {record}")


def unmarshall(record):
    return unmarshall_value({"M": record})
