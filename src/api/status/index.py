from http import HTTPStatus

import boto3
from event.environment import BaseEnvironment
from event.logging.logger import setup_logger
from event.logging.step_decorators import logging_step_decorators
from event.response.steps import response_steps
from event.step_chain import StepChain


class Environment(BaseEnvironment):
    DYNAMODB_TABLE: str


cache = {
    **Environment.build().dict(),
    "DYNAMODB_CLIENT": boto3.client("dynamodb"),
}
step_decorators = [*logging_step_decorators]
post_steps = [*response_steps]


class StatusNotOk(Exception):
    pass


def _status_check(data, cache) -> HTTPStatus:
    if cache["DYNAMODB_TABLE"] not in cache["DYNAMODB_CLIENT"].list_tables():
        raise StatusNotOk
    return HTTPStatus.OK


def handler(event: dict, context=None):
    setup_logger(service_name=__file__)

    api_chain = StepChain(step_chain=[_status_check], step_decorators=step_decorators)
    api_chain.run(cache=cache, init=event)

    response_chain = StepChain(step_chain=post_steps, step_decorators=step_decorators)
    response_chain.run(init=api_chain.result)
    return response_chain.result
