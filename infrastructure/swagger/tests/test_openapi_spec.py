import json
from pathlib import Path

import pytest
import yaml
from openapi3 import OpenAPI

PATH_TO_SWAGGER_BASE = Path(__file__).parent.parent


def flatten_json(data, parent_key="", separator="."):
    flat_dict = {}

    if isinstance(data, list):
        for index, item in enumerate(data):
            new_key = f"{parent_key}{separator}{index}" if parent_key else str(index)
            flat_dict.update(flatten_json(item, new_key, separator))
    elif isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            flat_dict.update(flatten_json(value, new_key, separator))
    else:
        flat_dict[parent_key] = data

    return flat_dict


@pytest.mark.parametrize(
    "swagger_file_path",
    PATH_TO_SWAGGER_BASE.glob("**/swagger.yaml"),
    ids=map(str, PATH_TO_SWAGGER_BASE.glob("**/swagger.yaml")),
)
def test_openapi_spec(swagger_file_path: Path):
    with open(swagger_file_path) as f:
        spec = yaml.safe_load(f.read())

    dead_ends = []
    for k, v in flatten_json(spec).items():
        if v is None:
            dead_ends.append(k)

    found_dead_ends = bool(dead_ends)
    assert (
        not found_dead_ends
    ), f"Found the following dead ends in the spec: {dead_ends}"

    api = OpenAPI(spec, validate=True)
    error_messages = [getattr(error, "message") for error in api.errors()]
    found_errors = bool(error_messages)
    assert not found_errors, json.dumps(error_messages, indent=4)
