from types import ModuleType

from api_utils.versioning.constants import VersioningStepArgs
from api_utils.versioning.steps import (
    get_largest_possible_version,
    get_steps_for_requested_version,
    versioning_steps,
)
from domain.logging.step_decorators import logging_step_decorators
from domain.response.steps import response_steps
from event.step_chain import StepChain

STEP_DECORATORS = [*logging_step_decorators]


def lower_case_keys(_dict: dict[str, str]):
    return {k.lower(): v for k, v in _dict.items()}


def execute_step_chain(
    event: dict, cache: dict, versioned_steps: dict[str, ModuleType]
):
    event["headers"] = lower_case_keys(event.get("headers", {}))

    version_chain = StepChain(
        step_chain=versioning_steps, step_decorators=STEP_DECORATORS
    )
    version_chain.run(
        init={
            VersioningStepArgs.EVENT: event,
            VersioningStepArgs.VERSIONED_STEPS: versioned_steps,
        }
    )

    version = None
    if isinstance(version_chain.result, Exception):
        result = version_chain.result
    else:
        version = version_chain.data[get_largest_possible_version]
        steps = version_chain.data[get_steps_for_requested_version]
        api_chain = StepChain(step_chain=steps, step_decorators=STEP_DECORATORS)
        api_chain.run(cache=cache, init=event)
        result = api_chain.result

    response_chain = StepChain(
        step_chain=response_steps, step_decorators=STEP_DECORATORS
    )
    response_chain.run(init=(result, version))
    return response_chain.result
