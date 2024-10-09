from types import ModuleType

from api_utils.versioning.constants import VERSIONING_STEP_ARGS
from api_utils.versioning.steps import (
    get_largest_possible_version,
    get_steps_for_requested_version,
    versioning_steps,
)
from domain.logging.step_decorators import logging_step_decorators
from domain.response.steps import response_steps
from domain.response.steps_old import response_steps as response_steps_old
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
            VERSIONING_STEP_ARGS.EVENT: event,
            VERSIONING_STEP_ARGS.VERSIONED_STEPS: versioned_steps,
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
    response_chain.run(init=(result, version, None))
    return response_chain.result


def execute_step_chain_fhir(
    event: dict, cache: dict, versioned_steps: dict[str, ModuleType]
):
    event["headers"] = lower_case_keys(event.get("headers", {}))

    version_chain = StepChain(
        step_chain=versioning_steps, step_decorators=STEP_DECORATORS
    )
    version_chain.run(
        init={
            VERSIONING_STEP_ARGS.EVENT: event,
            VERSIONING_STEP_ARGS.VERSIONED_STEPS: versioned_steps,
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
        step_chain=response_steps_old, step_decorators=STEP_DECORATORS
    )
    response_chain.run(init=(result, version, None))
    return response_chain.result


def execute_step_chain_with_location(
    event: dict, cache: dict, versioned_steps: dict[str, ModuleType]
):
    """After FHIR removed from everywhere can also remove this"""
    event["headers"] = lower_case_keys(event.get("headers", {}))

    version_chain = StepChain(
        step_chain=versioning_steps, step_decorators=STEP_DECORATORS
    )
    version_chain.run(
        init={
            VERSIONING_STEP_ARGS.EVENT: event,
            VERSIONING_STEP_ARGS.VERSIONED_STEPS: versioned_steps,
        }
    )

    version = None
    location = None
    if isinstance(version_chain.result, Exception):
        result = version_chain.result
    else:
        version = version_chain.data[get_largest_possible_version]
        steps = version_chain.data[get_steps_for_requested_version]
        api_chain = StepChain(step_chain=steps, step_decorators=STEP_DECORATORS)
        api_chain.run(cache=cache, init=event)
        if isinstance(api_chain.result, Exception):
            result = api_chain.result
        else:
            result, location = api_chain.result

    response_chain = StepChain(
        step_chain=response_steps_old, step_decorators=STEP_DECORATORS
    )
    response_chain.run(init=(result, version, location))
    return response_chain.result
