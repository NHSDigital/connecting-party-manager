from domain.logging.step_decorators import logging_step_decorators
from domain.response.steps import response_steps
from event.aws.client import dynamodb_client
from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.status.steps import steps
from event.step_chain import StepChain


class Environment(BaseEnvironment):
    DYNAMODB_TABLE: str


cache = {
    **Environment.build().dict(),
    "DYNAMODB_CLIENT": dynamodb_client(),
}
step_decorators = [*logging_step_decorators]
post_steps = [*response_steps]


def handler(event: dict, context=None):
    setup_logger(service_name=__file__)

    api_chain = StepChain(step_chain=steps, step_decorators=step_decorators)
    api_chain.run(cache=cache, init=event)

    response_chain = StepChain(step_chain=post_steps, step_decorators=step_decorators)
    response_chain.run(init=(api_chain.result, None, None))
    return response_chain.result
