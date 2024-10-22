from api_utils.api_step_chain import execute_step_chain
from event.logging.logger import setup_logger

from .src.v1.steps import steps as v1_steps

versioned_steps = {"1": v1_steps}
cache = {}


def handler(event: dict, context=None):
    setup_logger(service_name=__file__)
    return execute_step_chain(
        event=event,
        cache=cache,
        versioned_steps=versioned_steps,
    )
