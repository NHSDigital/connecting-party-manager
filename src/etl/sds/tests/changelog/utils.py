from collections import deque
from pathlib import Path
from typing import Any, Literal, Protocol

from domain.core.device import Device
from event.json import json_load, json_loads

PATH_TO_HERE = Path(__file__).parent / "changelog_components"


def read_ldif(relative_path: str):
    with open(PATH_TO_HERE / relative_path) as f:
        return f.read().strip("\n")


def create_modify_ldif(
    *relative_paths: str,
    device_type: Literal["accredited_system", "message_handling_system"],
):
    with open(PATH_TO_HERE / "modify" / device_type / "base.ldif") as f:
        base = f.read()

    components = list(
        map(lambda path: read_ldif(f"modify/{device_type}/{path}"), relative_paths)
    )
    return base.replace("<<TEMPLATE>>", "\n-\n".join(components))


class Handler(Protocol):
    def __call__(self, event, context) -> dict[str, any]: ...


class Scenario(Protocol):
    @property
    def extract_input(self) -> str: ...

    @property
    def database_initial_state(self) -> str: ...

    @property
    def extract_output(self) -> str: ...

    @property
    def transform_output(self) -> str: ...

    @property
    def load_output(self) -> str: ...

    @property
    def expected_errors(self) -> list[str]: ...


class _Scenario:
    def __init__(self, file_path: str, extract_input: list[str]):
        self.root = Path(file_path).parent
        self.name = self.root.name
        self.extract_input = "\n\n".join(extract_input)

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name == "expected_errors":
                expected_errors = []
                error_files = filter(
                    lambda path: path.suffix == ".error", self.root.iterdir()
                )
                for path in error_files:
                    with open(file=path) as f:
                        expected_errors.append(f.read())
                return expected_errors
            else:
                with open(self.root / f"{name}.json") as f:
                    return json_load(f)


obj_likes = (list, set, deque, tuple, dict)


def convert_list_likes(obj):
    if isinstance(obj, (list, set, deque, tuple)):
        _list = list if any(isinstance(item, obj_likes) for item in obj) else sorted
        _obj = _list(map(convert_list_likes, obj))
    elif isinstance(obj, dict):
        _obj = {k: convert_list_likes(v) for k, v in obj.items()}
    else:
        _obj = obj
    return _obj


def device_as_json_dict(device: Device) -> dict:
    _device: dict = device.state()
    _device.pop("id")
    _device["questionnaire_responses"] = {
        k: [
            json_loads(questionnaire_response.json())
            for _, questionnaire_response in questionnaire_responses.items()
        ]
        for k, questionnaire_responses in device.questionnaire_responses.items()
    }

    for questionnaire_responses in _device["questionnaire_responses"].values():
        for questionnaire_response in questionnaire_responses:
            questionnaire_response["created_on"] = "CREATED_ON"

    return _device


ADD_ACCREDITED_SYSTEM = read_ldif("add/accredited_system.ldif")
DELETE_ACCREDITED_SYSTEM = read_ldif("delete/accredited_system.ldif")
ADD_MESSAGE_HANDLING_SYSTEM = read_ldif("add/message_handling_system.ldif")
DELETE_MESSAGE_HANDLING_SYSTEM = read_ldif("delete/message_handling_system.ldif")
DELETE_UNKNOWN_ENTITY = read_ldif("delete/unknown_entity.ldif")
MODIFY_UNKNOWN_ENTITY = read_ldif("modify/unknown_entity.ldif")
ADD_ANOTHER_MESSAGE_HANDLING_SYSTEM_WITH_SAME_UNIQUE_IDENTIFIER = read_ldif(
    "add/message_handling_system.AnotherWithSameUniqueIdentifier.ldif"
)
