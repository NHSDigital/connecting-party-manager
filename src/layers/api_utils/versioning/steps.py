import math
from types import FunctionType

from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.step_chain import StepChain

from .constants import VersioningStepArgs
from .errors import VersionException
from .models import Event


@mark_validation_errors_as_inbound
def get_requested_version(data, cache=None):
    event = Event(**data[StepChain.INIT][VersioningStepArgs.EVENT])
    return event.headers.version


def get_largest_possible_version(data, cache=None) -> str:
    requested_version = data[get_requested_version]
    possible_versions = data[StepChain.INIT][VersioningStepArgs.VERSIONED_STEPS]
    integer_versions = map(int, possible_versions)
    possible_versions = [
        version
        for version in integer_versions
        if int(float(requested_version)) >= version
    ]
    largest_possible_version = max(possible_versions, default=math.inf)
    if not math.isfinite(largest_possible_version):
        raise VersionException(f"Version not supported: {requested_version}")
    return str(largest_possible_version)


def get_steps_for_requested_version(data, cache=None):
    steps_by_version = data[StepChain.INIT][VersioningStepArgs.VERSIONED_STEPS]
    largest_possible_version = data[get_largest_possible_version]
    return steps_by_version[largest_possible_version]


versioning_steps: list[FunctionType] = [
    get_requested_version,
    get_largest_possible_version,
    get_steps_for_requested_version,
]
