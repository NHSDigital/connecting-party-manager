import math
from importlib import import_module
from pathlib import Path
from types import FunctionType

from event.step_chain import StepChain

from .constants import API_ROOT_DIRNAME, VERSION_RE, VERSIONED_HANDLER_GLOB
from .errors import VersionException
from .models import LambdaEventForVersioning


def _module_path_from_file_path(file_path: Path):
    path = str(file_path.parent / file_path.stem)
    path_relative_to_api_root = Path(path[path.find(API_ROOT_DIRNAME) :])
    return ".".join(path_relative_to_api_root.parts)


def get_requested_version(data, cache=None):
    event = LambdaEventForVersioning(**data[StepChain.INIT]["event"])
    return event.headers.version


def get_steps_by_version(data, cache=None) -> dict[str, list[FunctionType]]:
    api_index_file_path = data[StepChain.INIT]["api_index_file_path"]
    versions_paths = Path(api_index_file_path).parent.glob(VERSIONED_HANDLER_GLOB)
    versioned_steps = {}
    for file_path in versions_paths:
        (version_number,) = VERSION_RE.match(file_path.parent.name).groups()
        module_path = _module_path_from_file_path(file_path)
        versioned_handler = import_module(module_path)
        versioned_steps[version_number] = versioned_handler.steps
    return versioned_steps


def get_largest_possible_version(data, cache=None) -> str:
    requested_version = data[get_requested_version]
    possible_versions = data[get_steps_by_version]
    integer_versions = map(int, possible_versions)
    possible_versions = [
        version
        for version in integer_versions
        if int(float(requested_version)) >= version
    ]
    largest_possible_version = max(possible_versions, default=math.inf)
    if not math.isfinite(largest_possible_version):
        raise VersionException("Version not supported")
    return str(largest_possible_version)


def get_steps_for_requested_version(data, cache=None):
    steps_by_version = data[get_steps_by_version]
    largest_possible_version = data[get_largest_possible_version]
    return steps_by_version[largest_possible_version]


versioning_steps: list[FunctionType] = [
    get_requested_version,
    get_steps_by_version,
    get_largest_possible_version,
    get_steps_for_requested_version,
]
