from pathlib import Path

from event.json import json_load

PATH_TO_TEST_DATA = Path(__file__).parent / "data"


def read_test_data(name: str) -> dict[str, any]:
    with open(PATH_TO_TEST_DATA / name) as f:
        return json_load(f)
