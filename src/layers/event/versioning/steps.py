import math
from types import FunctionType

from event.step_chain import StepChain

from .constants import VERSIONING_STEP_ARGS
from .errors import VersionException
from .models import LambdaEventForVersioning


def get_requested_version(data, cache=None):
    event = LambdaEventForVersioning(**data[StepChain.INIT][VERSIONING_STEP_ARGS.EVENT])
    return event.headers.version


def get_largest_possible_version(data, cache=None) -> str:
    requested_version = data[get_requested_version]
    possible_versions = data[StepChain.INIT][VERSIONING_STEP_ARGS.VERSIONED_STEPS]
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
    steps_by_version = data[StepChain.INIT][VERSIONING_STEP_ARGS.VERSIONED_STEPS]
    largest_possible_version = data[get_largest_possible_version]
    return steps_by_version[largest_possible_version]


versioning_steps: list[FunctionType] = [
    get_requested_version,
    get_largest_possible_version,
    get_steps_for_requested_version,
]
