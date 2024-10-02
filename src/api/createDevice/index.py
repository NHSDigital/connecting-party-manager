from api_utils.api_step_chain import execute_step_chain_with_location
from types import ModuleType

from api_utils.versioning.constants import VERSIONING_STEP_ARGS
from api_utils.versioning.steps import (
    get_largest_possible_version,
    get_steps_for_requested_version,
    versioning_steps,
)
from domain.logging.step_decorators import logging_step_decorators
from domain.response.steps_old import response_steps
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from event.logging.logger import setup_logger

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
    return execute_step_chain_with_location(
        event=event,
        cache=cache,
        versioned_steps=versioned_steps,
    )
