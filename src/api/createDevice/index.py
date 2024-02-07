from types import ModuleType

from domain.logging.step_decorators import logging_step_decorators
from domain.response.steps import response_steps
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.step_chain import StepChain
from event.versioning.constants import VERSIONING_STEP_ARGS
from event.versioning.steps import (
    get_largest_possible_version,
    get_steps_for_requested_version,
    versioning_steps,
)

from .src.v1.steps import steps as v1_steps


class Environment(BaseEnvironment):
    DYNAMODB_TABLE: str


versioned_steps = {"1": v1_steps}
cache = {
    **Environment.build().dict(),
    "DYNAMODB_CLIENT": dynamodb_client(),
}


def handler(event: dict, context=None):
    setup_logger(service_name=__file__)
    return execute_step_chain(
        event=event,
        cache=cache,
        versioned_steps=versioned_steps,
    )


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
        step_chain=response_steps, step_decorators=STEP_DECORATORS
    )
    response_chain.run(init=(result, version, location))
    return response_chain.result
