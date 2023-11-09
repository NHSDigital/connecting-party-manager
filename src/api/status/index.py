from http import HTTPStatus

from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.logging.step_decorators import logging_step_decorators
from event.response.steps import response_steps
from event.step_chain import StepChain


class Environment(BaseEnvironment):
    DYNAMODB_TABLE: str


cache = {**Environment.build().dict()}
step_decorators = [*logging_step_decorators]
post_steps = [*response_steps]


def _status_check(data, cache):
    return HTTPStatus.OK


def handler(event: dict, context=None):
    setup_logger(service_name=__file__)

    step_chain = StepChain(step_chain=[_status_check], step_decorators=step_decorators)
    step_chain.run(cache=cache, init=event)

    post_step_chain = StepChain(step_chain=post_steps, step_decorators=step_decorators)
    post_step_chain.run(init=step_chain.result)
    return post_step_chain.result
